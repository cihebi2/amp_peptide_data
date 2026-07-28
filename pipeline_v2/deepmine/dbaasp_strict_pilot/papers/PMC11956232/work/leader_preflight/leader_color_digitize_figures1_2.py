#!/usr/bin/env python3
"""Reproducible color-segmentation scaffold for PMC11956232 Figures 1 and 2.

This is leader-owned calibration evidence, not a terminal scientific artifact.
Canonical worker-3 must visually/source-review every point and worker-2/6 must
preserve approximate status, uncertainty, overlaps, and omissions.
"""
from __future__ import annotations
import hashlib, json, colorsys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
IMGDIR=HERE/'figure_crops_300dpi'
OUT=HERE/'leader_color_digitized_figures1_2.json'
DOSES={
 'navy':{'dose_fold_mic':0.25,'hue_range':[0.58,0.72]},
 'cyan':{'dose_fold_mic':0.5,'hue_range':[0.45,0.58]},
 'yellow':{'dose_fold_mic':1.0,'hue_range':[0.10,0.22]},
 'red':{'dose_fold_mic':2.0,'hue_range':'h<0.04 or h>=0.90'},
}
STRAINS=['DC 5147','DC 6729','DC 7956','DC 8439','DC 10495','DC 11712','DC 11722','DC 11723','DC 12843','DC 13281']
F1_LEFT=[215,622,1030,1437,1843]; F1_RIGHT=[503,910,1317,1725,2130]
F2_LEFT=[196,599,1002,1428,1840]; F2_RIGHT=[487,890,1293,1720,2131]
F1_YMAX=[1.0,1.0,1.0,1.0,0.8,1.0,1.0,1.2,1.2,1.0]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hsv_masks(rgb):
 a=rgb.astype(float)/255.0
 flat=a.reshape(-1,3)
 hsv=np.array([colorsys.rgb_to_hsv(*x) for x in flat]).reshape(a.shape)
 h,s,v=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
 common=(s>0.22)&(v>0.20)&(v<0.99)
 return {
  'navy':common&(h>=0.58)&(h<0.72)&(v<0.62),
  'cyan':common&(h>=0.45)&(h<0.58),
  'yellow':common&(h>=0.10)&(h<0.22)&(v>0.55),
  'red':common&((h<0.04)|(h>=0.90))&(v>0.55),
 }
def x_positions(left,right,times,max_t): return [left+t/max_t*(right-left) for t in times]
def value(y,top,bottom,ymax): return round(max(0,min(ymax,(bottom-y)/(bottom-top)*ymax)),3)
def extract(fig,image_path,times,panels,unit):
 rgb=np.array(Image.open(image_path).convert('RGB')); masks=hsv_masks(rgb); rows=[]; missing=[]
 for panel in panels:
  xs=x_positions(panel['x_left'],panel['x_right'],times,times[-1])
  per_color={}
  for color,d in DOSES.items():
   crow=[]
   for t,x in zip(times,xs):
    xc=round(x); band=masks[color][panel['y_top']:panel['y_bottom']+1,max(0,xc-10):xc+11]
    ys=np.where(band)[0]+panel['y_top']
    # reject antialiased text/noise by keeping the densest local y neighborhood
    if len(ys):
     hist=np.bincount(ys,minlength=rgb.shape[0]); center=int(hist.argmax()); local=ys[np.abs(ys-center)<=5]
     y=float(np.median(local)); count=int(len(local)); status='color_marker_or_line_local_median'
    else:
     y=None; count=0; status='missing_color_pixels_requires_source_review'; missing.append({'figure':fig,'panel':panel['panel'],'color':color,'time':t})
    crow.append({'figure':fig,'panel':panel['panel'],'target':'Escherichia coli '+panel['strain']+' (CREC)','color':color,'dose_fold_mic':d['dose_fold_mic'],'time':t,'time_unit':'h' if fig=='Figure 1' else 'min','raw_value':None if y is None else value(y,panel['y_top'],panel['y_bottom'],panel['y_max']),'raw_unit':unit,'image_coordinate_px':{'x':round(x,1),'y':None if y is None else round(y,1)},'pixel_count_local':count,'digitization_status':status,'missing_reason':None if y is not None else 'no_color_pixels_in_local_x_band','exact_vs_approximate_status':'approximate_color_segmented_from_300dpi_pdf_render','coordinate_uncertainty_px':7,'raw_value_uncertainty':round(panel['y_max']/(panel['y_bottom']-panel['y_top'])*8,3),'treatment_control_role':'treatment'})
   per_color[color]=crow
  # Resolve only visually defensible overlaps. Curves share the time-zero
  # baseline; later high-dose curves can also be exactly superimposed at the
  # Figure 1 assay floor or the Figure 2 detection limit.
  for time_index, time_value in enumerate(times):
   visible=[x[time_index]['raw_value'] for x in per_color.values() if x[time_index]['raw_value'] is not None]
   if not visible:
    continue
   shared=None
   status=None
   if time_index==0:
    shared=round(float(np.median(visible)),3)
    status='shared_visible_time_zero_baseline_due_to_curve_overlap'
   elif max(visible)-min(visible)<=2*panel['y_max']/(panel['y_bottom']-panel['y_top'])*8:
    shared=round(float(np.median(visible)),3)
    status='shared_visible_same_timepoint_value_due_to_curve_overlap'
   elif fig=='Figure 1' and min(visible)<=0.12*panel['y_max']:
    shared=round(float(min(visible)),3)
    status='shared_visible_assay_floor_due_to_high_dose_curve_overlap'
   elif fig=='Figure 2' and min(visible)<=2.2:
    shared=round(float(min(visible)),3)
    status='shared_visible_detection_limit_due_to_curve_overlap'
   if shared is not None:
    for x in per_color.values():
     if x[time_index]['raw_value'] is None:
      x[time_index]['raw_value']=shared
      x[time_index]['digitization_status']=status
      x[time_index]['missing_reason']=None
  for color in DOSES: rows.extend(per_color[color])
 return rows,missing

def main():
 f1=[]; f2=[]
 for i,strain in enumerate(STRAINS):
  row=i//5; col=i%5
  f1.append({'panel':chr(65+i),'strain':strain,'x_left':F1_LEFT[col],'x_right':F1_RIGHT[col],'y_top':407 if row==0 else 829,'y_bottom':600 if row==0 else 1021,'y_max':F1_YMAX[i]})
  f2.append({'panel':chr(65+i),'strain':strain,'x_left':F2_LEFT[col],'x_right':F2_RIGHT[col],'y_top':246 if row==0 else 707,'y_bottom':439 if row==0 else 901,'y_max':8.0})
 p1=IMGDIR/'figure1.png'; p2=IMGDIR/'figure2.png'
 r1,m1=extract('Figure 1',p1,[0,2,4,6,8,10,12,20,24],f1,'OD600')
 r2,m2=extract('Figure 2',p2,[0,10,20,30,40,50,60],f2,'log10 CFU/mL')
 u1=[{'panel':x['panel'],'color':x['color'],'time':x['time'],'reason':x['missing_reason']} for x in r1 if x['raw_value'] is None]
 u2=[{'panel':x['panel'],'color':x['color'],'time':x['time'],'reason':x['missing_reason']} for x in r2 if x['raw_value'] is None]
 payload={'paper_id':'PMC11956232','artifact_role':'leader_color_segmentation_scaffold_requires_canonical_worker3_source_review','method':{'source':'300 dpi PDF render','color_segmentation':'HSV masks with local densest-y median in +/-10 px x bands','axis_mapping':'linear panel-specific coordinates from long black axis pixel runs plus visual confirmation','overlap_resolution':'time-zero, same-timepoint, Figure 1 assay-floor, and Figure 2 detection-limit rules; unresolved values remain null','limitations':'approximate; error bars are not values; hidden overlapping curves may remain missing and must not be fabricated'},'figures':{'Figure 1':{'source_image':str(p1.relative_to(HERE.parents[7])),'sha256':sha(p1),'expected_observations':360,'panels':f1,'initial_missing_color_segments':m1,'initial_missing_count':len(m1),'unresolved_missing':u1,'unresolved_missing_count':len(u1),'observations':r1},'Figure 2':{'source_image':str(p2.relative_to(HERE.parents[7])),'sha256':sha(p2),'expected_observations':280,'panels':f2,'initial_missing_color_segments':m2,'initial_missing_count':len(m2),'unresolved_missing':u2,'unresolved_missing_count':len(u2),'observations':r2}},'total_observations':len(r1)+len(r2),'total_initial_missing_color_segments':len(m1)+len(m2),'total_unresolved_missing_after_overlap_rules':len(u1)+len(u2)}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'output':str(OUT),'figure1_rows':len(r1),'figure2_rows':len(r2),'total_rows':len(r1)+len(r2),'initial_missing_color_segments':payload['total_initial_missing_color_segments'],'unresolved_missing_values':payload['total_unresolved_missing_after_overlap_rules'],'figure1_unique_values':len({x['raw_value'] for x in r1 if x['raw_value'] is not None}),'figure2_unique_values':len({x['raw_value'] for x in r2 if x['raw_value'] is not None})},indent=2))
if __name__=='__main__': main()
