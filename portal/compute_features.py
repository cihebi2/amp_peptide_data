#!/usr/bin/env python3
"""Compute physicochemical features for every distinct peptide sequence in atlas.db.
Pure stdlib (no biopython). Writes a `features` table keyed by sequence.

Features: length, molecular weight, net charge (pH 7.4), isoelectric point (pI),
GRAVY hydrophobicity (Kyte-Doolittle), hydrophobic-residue fraction, aromatic fraction,
Eisenberg hydrophobic moment (μH, α-helix 100°/residue) and normalized μH, cationic flag.

Run:  python3 compute_features.py [--db atlas.db]
"""
import sqlite3, argparse, math, re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# monoisotopic-ish average residue masses (Da), water added once
_MW = {"A":71.08,"R":156.19,"N":114.10,"D":115.09,"C":103.14,"E":129.12,"Q":128.13,
       "G":57.05,"H":137.14,"I":113.16,"L":113.16,"K":128.17,"M":131.19,"F":147.18,
       "P":97.12,"S":87.08,"T":101.10,"W":186.21,"Y":163.18,"V":99.13}
# Kyte-Doolittle hydropathy
_KD = {"A":1.8,"R":-4.5,"N":-3.5,"D":-3.5,"C":2.5,"E":-3.5,"Q":-3.5,"G":-0.4,"H":-3.2,
       "I":4.5,"L":3.8,"K":-3.9,"M":1.9,"F":2.8,"P":-1.6,"S":-0.8,"T":-0.7,"W":-0.9,
       "Y":-1.3,"V":4.2}
# Eisenberg consensus hydrophobicity (for hydrophobic moment)
_EIS = {"A":0.62,"R":-2.53,"N":-0.78,"D":-0.90,"C":0.29,"E":-0.74,"Q":-0.85,"G":0.48,
        "H":-0.40,"I":1.38,"L":1.06,"K":-1.50,"M":0.64,"F":1.19,"P":0.12,"S":-0.18,
        "T":-0.05,"W":0.81,"Y":0.26,"V":1.08}
_AROMATIC = set("FWY")
# pKa (EMBOSS) for pI / charge
_PKA_POS = {"K":10.8,"R":12.5,"H":6.5}   # + when protonated
_PKA_NEG = {"D":3.9,"E":4.1,"C":8.5,"Y":10.1}
_NTERM, _CTERM = 8.6, 3.6
_STD = set(_MW)


def clean_seq(s):
    return re.sub(r"[^A-Z]", "", (s or "").upper())


def charge_at(seq, pH):
    pos = 1.0 / (1.0 + 10 ** (pH - _NTERM))
    for aa, pk in _PKA_POS.items():
        pos += seq.count(aa) * (1.0 / (1.0 + 10 ** (pH - pk)))
    neg = 1.0 / (1.0 + 10 ** (_CTERM - pH))
    for aa, pk in _PKA_NEG.items():
        neg += seq.count(aa) * (1.0 / (1.0 + 10 ** (pk - pH)))
    return pos - neg


def isoelectric_point(seq):
    lo, hi = 0.0, 14.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if charge_at(seq, mid) > 0:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 2)


def hydrophobic_moment(seq, angle_deg=100.0):
    """Eisenberg μH over the whole sequence (α-helix periodicity)."""
    ang = math.radians(angle_deg)
    sx = sum(_EIS.get(a, 0.0) * math.cos(i * ang) for i, a in enumerate(seq))
    sy = sum(_EIS.get(a, 0.0) * math.sin(i * ang) for i, a in enumerate(seq))
    return math.sqrt(sx * sx + sy * sy)


_CLEAN = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]{2,}$")


def features(seq):
    # Only well-defined LINEAR sequences of the 20 standard residues.
    # Branched/modified constructs (parentheses, digits, '-', lowercase, X/B/Z/U) are skipped —
    # physicochemical descriptors are not meaningful for them.
    s = (seq or "").strip().upper()
    if not _CLEAN.fullmatch(s):
        return None
    n = len(s)
    mw = sum(_MW[a] for a in s) + 18.02
    hyd_frac = sum(1 for a in s if a in "AILMFWVC") / n
    arom = sum(1 for a in s if a in _AROMATIC) / n
    gravy = sum(_KD[a] for a in s) / n
    net = charge_at(s, 7.4)
    muh = hydrophobic_moment(s)
    return {
        "length": n, "mw": round(mw, 1), "net_charge": round(net, 2),
        "pI": isoelectric_point(s), "gravy": round(gravy, 3),
        "hydrophobic_frac": round(hyd_frac, 3), "aromatic_frac": round(arom, 3),
        "mu_h": round(muh, 2), "mu_h_per_res": round(muh / n, 3),
        "cationic": 1 if net >= 2 else 0,
    }


def compute_into(db):
    """(Re)build the `features` table on an open sqlite connection. Returns (n_seen, n_computed, n_skipped)."""
    db.execute("DROP TABLE IF EXISTS features")
    db.execute("""CREATE TABLE features(sequence TEXT PRIMARY KEY, length INT, mw REAL, net_charge REAL,
        pI REAL, gravy REAL, hydrophobic_frac REAL, aromatic_frac REAL, mu_h REAL, mu_h_per_res REAL, cationic INT)""")
    seqs = [r[0] for r in db.execute("SELECT DISTINCT sequence FROM activity WHERE sequence<>''")]
    rows, skipped = [], 0
    for sq in seqs:
        f = features(sq)
        if not f:
            skipped += 1
            continue
        rows.append((sq, f["length"], f["mw"], f["net_charge"], f["pI"], f["gravy"],
                     f["hydrophobic_frac"], f["aromatic_frac"], f["mu_h"], f["mu_h_per_res"], f["cationic"]))
    db.executemany("INSERT OR IGNORE INTO features VALUES(?,?,?,?,?,?,?,?,?,?,?)", rows)
    db.execute("CREATE INDEX i_feat_seq ON features(sequence)")
    db.commit()
    return len(seqs), len(rows), skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=HERE / "atlas.db")
    args = ap.parse_args()
    db = sqlite3.connect(args.db)
    seen, comp, skipped = compute_into(db)
    print(f"sequences seen: {seen}  features computed: {comp}  skipped(non-standard/short): {skipped}")
    # quick sanity
    for r in db.execute("SELECT sequence,length,net_charge,pI,gravy,mu_h_per_res,cationic FROM features LIMIT 3"):
        print("  ", r[0][:24], "len", r[1], "charge", r[2], "pI", r[3], "gravy", r[4], "muH/res", r[5], "cationic", r[6])
    cat = db.execute("SELECT COUNT(*) FROM features WHERE cationic=1").fetchone()[0]
    print(f"cationic (net≥+2): {cat}/{len(rows)}")
    db.close()


if __name__ == "__main__":
    main()
