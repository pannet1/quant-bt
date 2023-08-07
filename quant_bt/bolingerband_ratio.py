from omspy_brokers.angel_one import AngelOne
from toolkit.fileutils import Fileutils
from indicators.bolingerband_ratio import indicator
from plots.bolingerband_ratio import plot

cred = Fileutils().get_lst_fm_yml("../../../angel.yaml")
ao = AngelOne(**cred)
if ao.authenticate():
    ao.profile()

lst_close = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
             12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
val = indicator(lst_close, period=20)
plot(val)
