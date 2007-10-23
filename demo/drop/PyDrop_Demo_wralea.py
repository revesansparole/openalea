
# This file has been generated at $TIME

from openalea.core import *

def register_packages(pkgmanager):
    
    metainfo = {'description': 'PyDrop Demo', 'license': '', 'url': '', 'version': '', 'authors': 'Samuel Dufour-Kowalski, Francois Bussiere', 'institutes': 'INRA'} 
    pkg = UserPackage("Demo.PyDrop", metainfo)

    

    nf = CompositeNodeFactory(name='pydrop_simple2', 
                              description='', 
                              category='Ecophysiology',
                              doc='',
                              inputs=[],
                              outputs=[],
                              elt_factory={2: ('pydrop', 'ReadB3D'), 3: ('pydrop', 'DropTri'), 4: ('pydrop', 'DropDisplay'), 5: ('pydrop', 'DropInt'), 6: ('pydrop', 'DropSummary'), 7: ('Catalog.Python', 'print'), 8: ('Catalog.Python', 'fwrite'), 9: ('System', 'annotation'), 10: ('System', 'annotation'), 11: ('System', 'annotation'), 12: ('System', 'annotation'), 13: ('System', 'annotation'), 14: ('System', 'annotation'), 15: ('System', 'annotation'), 16: ('System', 'annotation')},
                              elt_connections={140713792: (2, 0, 3, 0), 140713828: (5, 0, 4, 1), 140713864: (3, 0, 6, 0), 140713804: (5, 0, 6, 1), 140713840: (6, 0, 7, 0), 140713876: (6, 0, 8, 0), 140713816: (3, 0, 4, 0), 140713852: (3, 0, 5, 0)},
                              elt_data={2: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'ReadB3D', 'posx': 408.75, 'posy': 266.25, 'minimal': False}, 3: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropTri', 'posx': 430.0, 'posy': 356.25, 'minimal': False}, 4: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropDisplay', 'posx': 427.5, 'posy': 576.25, 'minimal': False}, 5: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropInt', 'posx': 531.25, 'posy': 468.75, 'minimal': False}, 6: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropSummary', 'posx': 193.75, 'posy': 567.5, 'minimal': False}, 7: {'lazy': False, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'print', 'posx': 263.75, 'posy': 656.25, 'minimal': False}, 8: {'lazy': False, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'fwrite', 'posx': 157.5, 'posy': 653.75, 'minimal': False}, 9: {'txt': 'Text Output', 'posx': 25.0, 'posy': 600.0}, 10: {'txt': '3D Output', 'posx': 451.25, 'posy': 643.75}, 11: {'txt': 'Read Digit file', 'posx': 556.25, 'posy': 266.25}, 12: {'txt': 'Mesh', 'posx': 556.25, 'posy': 356.25}, 13: {'txt': 'Rain Inteception', 'posx': 705.0, 'posy': 476.25}, 14: {'txt': 'Rain interception with PyDrop', 'posx': 426.25, 'posy': 105.0}, 15: {'txt': 'Authors : Samuel Dufour-Kowalski, Francois Bussiere', 'posx': 427.5, 'posy': 133.75}, 16: {'txt': 'Intitute : INRA', 'posx': 427.5, 'posy': 161.25}, '__out__': {'priority': 0, 'caption': 'Out', 'lazy': True, 'posx': 20.0, 'posy': 250.0}, '__in__': {'priority': 0, 'caption': 'In', 'lazy': True, 'posx': 20.0, 'posy': 5.0}},
                              elt_value={2: [(0, "''")], 3: [(1, "'Plant'")], 4: [(2, '30.0')], 5: [(1, '10'), (2, '10'), (3, '30'), (4, '30.0')], 6: [], 7: [], 8: [(1, "''"), (2, "'w'")], 9: [], 10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: [], '__out__': [], '__in__': []},
                              lazy=True,
                              )

    pkg.add_factory(nf)


    nf = CompositeNodeFactory(name='pydrop_simple', 
                              description='simple demo of pydrop', 
                              category='Ecophysiology',
                              doc='',
                              inputs=[],
                              outputs=[],
                              elt_factory={2: ('pydrop', 'ReadB3D'), 3: ('pydrop', 'DropTri'), 4: ('pydrop', 'DropDisplay'), 5: ('pydrop', 'DropInt'), 10: ('System', 'annotation'), 11: ('System', 'annotation'), 12: ('System', 'annotation'), 13: ('System', 'annotation'), 14: ('System', 'annotation'), 15: ('System', 'annotation'), 16: ('System', 'annotation')},
                              elt_connections={140713864: (2, 0, 3, 0), 140713852: (3, 0, 4, 0), 140713876: (3, 0, 5, 0), 140713840: (5, 0, 4, 1)},
                              elt_data={2: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'ReadB3D', 'posx': 408.75, 'posy': 266.25, 'minimal': False}, 3: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropTri', 'posx': 430.0, 'posy': 356.25, 'minimal': False}, 4: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropDisplay', 'posx': 427.5, 'posy': 576.25, 'minimal': False}, 5: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropInt', 'posx': 531.25, 'posy': 468.75, 'minimal': False}, 10: {'txt': '3D Output', 'posx': 451.25, 'posy': 643.75}, 11: {'txt': 'Read Digit file', 'posx': 556.25, 'posy': 266.25}, 12: {'txt': 'Mesh', 'posx': 556.25, 'posy': 356.25}, 13: {'txt': 'Rain Inteception', 'posx': 705.0, 'posy': 476.25}, 14: {'txt': 'Rain interception with PyDrop', 'posx': 426.25, 'posy': 105.0}, 15: {'txt': 'Authors : Samuel Dufour-Kowalski, Francois Bussiere', 'posx': 427.5, 'posy': 133.75}, 16: {'txt': 'Intitute : INRA', 'posx': 427.5, 'posy': 161.25}, '__out__': {'priority': 0, 'caption': 'Out', 'lazy': True, 'posx': 20.0, 'posy': 250.0}, '__in__': {'priority': 0, 'caption': 'In', 'lazy': True, 'posx': 20.0, 'posy': 5.0}},
                              elt_value={2: [(0, "''")], 3: [(1, "'Plant'")], 4: [(2, '30.0')], 5: [(1, '10'), (2, '10'), (3, '30'), (4, '30.0')], 10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: [], '__out__': [], '__in__': []},
                              lazy=True,
                              )

    pkg.add_factory(nf)


    nf = CompositeNodeFactory(name='pydrop_planter', 
                              description='', 
                              category='Ecophysiology',
                              doc='',
                              inputs=[],
                              outputs=[],
                              elt_factory={2: ('pydrop', 'DropDB'), 3: ('pydrop', 'Planter'), 4: ('pydrop', 'ListBuilder'), 5: ('pydrop', 'ListBuilder'), 6: ('Catalog.Python', 'zip'), 7: ('Catalog.Python', 'len'), 8: ('Catalog.Math', 'randlist'), 9: ('PlantGL Visualization', 'plot3D'), 10: ('pydrop', 'DropInt'), 11: ('pydrop', 'DropDisplay'), 12: ('Catalog.Data', 'int'), 13: ('System', 'annotation'), 14: ('System', 'annotation'), 15: ('System', 'annotation'), 16: ('System', 'annotation'), 17: ('spatial', 'Spatial Distribution'), 18: ('pydrop', 'to_pgl_scene'), 19: ('System', 'annotation'), 20: ('System', 'annotation'), 21: ('Catalog.Data', 'int'), 22: ('System', 'annotation'), 23: ('System', 'annotation'), 24: ('System', 'annotation'), 25: ('System', 'annotation'), 26: ('System', 'annotation'), 27: ('System', 'annotation')},
                              elt_connections={137523008: (7, 0, 8, 1), 137523056: (18, 0, 9, 0), 137523044: (5, 0, 3, 0), 137523080: (17, 1, 6, 1), 137523020: (3, 0, 10, 0), 137522924: (17, 0, 6, 0), 137522912: (6, 0, 3, 1), 137522960: (2, 1, 7, 0), 137522984: (8, 0, 4, 1), 137523032: (12, 0, 8, 2), 137522900: (2, 0, 5, 0), 137522948: (3, 0, 11, 0), 137522996: (2, 1, 4, 0), 137522936: (4, 0, 5, 1), 137523092: (10, 0, 11, 1), 137522972: (3, 0, 18, 0), 137522888: (21, 0, 11, 2), 137523068: (12, 0, 17, 0)},
                              elt_data={2: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropDB', 'posx': 115.86861043471131, 'posy': -149.21708446423139, 'minimal': False}, 3: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'Planter', 'posx': 233.42675991852275, 'posy': 263.16985146336066, 'minimal': False}, 4: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'Plant Names', 'posx': 134.53792162963725, 'posy': 44.144678206707567, 'minimal': False}, 5: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'extract', 'posx': 75.354355250680015, 'posy': 113.49552168746209, 'minimal': False}, 6: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'zip', 'posx': 362.31407283414268, 'posy': 195.52335211360534, 'minimal': False}, 7: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'len', 'posx': 262.88986027243709, 'posy': -91.080422685274698, 'minimal': False}, 8: {'lazy': False, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'randlist', 'posx': 259.09958616619883, 'posy': -15.748670519607739, 'minimal': False}, 9: {'lazy': False, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'plot3D', 'posx': 30.0, 'posy': 428.75, 'minimal': False}, 10: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropInt', 'posx': 410.0, 'posy': 306.25, 'minimal': False}, 11: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'DropDisplay', 'posx': 226.37756131066243, 'posy': 421.48389262700346, 'minimal': False}, 12: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': '20', 'posx': 388.77480395858146, 'posy': -55.478761396373997, 'minimal': False}, 13: {'txt': 'PyDrop Demo : Rain interception on banana plants', 'posx': 620.0, 'posy': -173.75}, 14: {'txt': 'Number of plants', 'posx': 439.42195027659267, 'posy': -54.132057014823317}, 15: {'txt': 'Drop Viewer', 'posx': 229.73027556676806, 'posy': 475.78945235625059}, 16: {'txt': '(X,Y) Positions', 'posx': 711.25, 'posy': 77.5}, 17: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'Spatial Distribution', 'posx': 527.5084836170563, 'posy': 76.046860011986269, 'minimal': False}, 18: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'to_pgl_scene', 'posx': 21.25, 'posy': 362.5, 'minimal': False}, 19: {'txt': 'Rain interception', 'posx': 543.75, 'posy': 306.25}, 20: {'txt': 'Banana plants Database', 'posx': 208.75, 'posy': -143.75}, 21: {'lazy': True, 'hide': True, 'port_hide_changed': set([]), 'priority': 0, 'caption': 'int', 'posx': 440.34090909090907, 'posy': 393.93939393939394, 'minimal': False}, 22: {'txt': 'Stemflow Reduction', 'posx': 500.11363636363637, 'posy': 396.780303030303}, 23: {'txt': 'Authors : Samuel Dufour-Kowalski', 'posx': 623.75, 'posy': -106.25}, 24: {'txt': 'Institutes : INRA', 'posx': 627.5, 'posy': -81.25}, 25: {'txt': 'Packages : PyDrop', 'posx': 623.75, 'posy': -132.5}, 26: {'txt': 'Choose randomly plants', 'posx': 261.25, 'posy': 46.25}, 27: {'txt': 'PlantGL Viewer', 'posx': -3.75, 'posy': 475.0}, '__out__': {'priority': 0, 'caption': 'Out', 'lazy': True, 'posx': 20.0, 'posy': 250.0}, '__in__': {'priority': 0, 'caption': 'In', 'lazy': True, 'posx': 20.0, 'posy': 5.0}},
                              elt_value={2: [(0, "'/home/sdufour/duclos.ddb'")], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [(0, '0')], 9: [], 10: [(1, '10'), (2, '10'), (3, '30'), (4, '30.0')], 11: [], 12: [(0, '20')], 13: [], 14: [], 15: [], 16: [], 17: [(1, '[0, 400]'), (2, '[0, 400]'), (3, "'Regular'"), (4, "{'cluster': 5, 'cluster_radius': 100}")], 18: [], 19: [], 20: [], 21: [(0, '18')], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], '__out__': [], '__in__': []},
                              lazy=True,
                              )

    pkg.add_factory(nf)


    pkgmanager.add_package(pkg)


