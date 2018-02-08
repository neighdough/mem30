import pandas as pd
import geopandas as gpd
import seaborn as sns
from caeser import utils
import matplotlib.pyplot as plt

engine = utils.connect(**utils.connection_properties('caeser-geo.memphis.edu', 
                                db='memphis_30'))
#bg = pd.read_sql('select * from tiger_bg_2016', engine)
#p14 = pd.read_sql("""select * from sca_parcels_2014 p join (select geoid, wkb_geometry,
#                        aland*0.000247105 aland from tiger_bg_2016) bg
#                        on st_within(st_centroid(p.wkb_geometry),bg.wkb_geometry)""", 
#                        engine)
#
#bg_acres = pd.read_sql("""select geoid, sum(calc_acre) acres from sca_parcels_2014 p 
#                            join (select geoid, wkb_geometry from tiger_bg_2016) bg
#                            on st_within(st_centroid(p.wkb_geometry), bg.wkb_geometry)
#                            group by geoid""", engine)
#

p14 = pd.read_sql("""select * from sca_parcels_2014""",engine)

emp14 = pd.read_sql("""select substring(id,1,12) geoid, sum(c000) tot_emp from otm_lodes_2014
                        group by geoid""", engine)

pop = pd.read_sql("""select * from nhgis_pop""", engine)

#area_res = p14[p14.livunit > 0.][['bgid', 'livunit', 'calc_acre']]
#area_res_grp = area_res.groupby('bgid')['calc_acre'].sum().reset_index()
#area_res_grp.rename(columns={'calc_acre':'res_acre'}, inplace=True)
bg = p14.groupby('bgid').agg({'livunit':'sum','calc_acre':'sum'}).reindex()
bg['lu_netden'] = bg.livunit / bg.calc_acre
#bg = bg.merge(area_res_grp, how='outer', right_on='bgid', left_index=True)

bg = bg.merge(emp14, right_on='geoid', how='outer',left_index=True)
bg['emp_netden'] = bg.tot_emp / bg.calc_acre

bg = bg.merge(pop[['geoid','pop00','pop10']])
bg['pop00_netden'] = bg.pop00 / bg.calc_acre
bg['pop10_netden'] = bg.pop10 / bg.calc_acre

pct_change = lambda row: ((row['pop10_netden']/row['pop00_netden'])\
        /row['pop00_netden'])*100 if row['pop00_netden'] > 0 else None
bg['pct_chg_density'] = bg.apply(pct_change)



