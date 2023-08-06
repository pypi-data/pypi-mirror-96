from gravity_core_api.main import GCSE
from wsqluse.wsqluse import Wsqluse

sqlshell = Wsqluse('wdb', 'watchman', 'hect0r1337', '192.168.100.109')
gcse = GCSE('0.0.0.0', 2295, sqlshell, debug=True)
gcse.launch_mainloop()