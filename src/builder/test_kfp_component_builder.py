from notebook import Notebook
from kfp_component import KfpComponent
from kfp_component_builder import KfpComponentBuilder


kfpcb = KfpComponentBuilder('../../test/notebooks/input-postgresql.ipynb')
print(kfpcb.get_yaml())