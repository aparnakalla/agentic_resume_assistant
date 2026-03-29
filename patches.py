import sys
import types

if 'pkg_resources' not in sys.modules:
    pkg_resources = types.ModuleType('pkg_resources')
    pkg_resources.get_distribution = lambda name: type('D', (), {'version': '0.0.0'})()
    pkg_resources.DistributionNotFound = Exception
    pkg_resources.RequirementParseError = Exception
    sys.modules['pkg_resources'] = pkg_resources
