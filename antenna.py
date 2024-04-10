import os

import pyaedt
import tempfile
import matplotlib.pyplot as plt
from pyaedt.modeler.advanced_cad.stackup_3d import Stackup3D
from pyaedt import Hfss


# Use the 2023R2 release of HFSS.

non_graphical = False  # Set to False to launch the AEDT UI.
desktop_version = "2023.1"
length_units = "mm"
freq_units = "GHz"
'''H = 1.6
L0 = 28
W0 = 37.26
L1 = 7
Length = 30.6'''

tmpdir = tempfile.TemporaryDirectory(suffix="_aedt")
project_folder = tmpdir.name
Antenna = os.path.join(project_folder, "antenna")

# Launch HFSS
# -----------
#

hfss = pyaedt.Hfss(projectname=Antenna,
                   solution_type="Driven Modal",
                   #designname="patch",
                   non_graphical=non_graphical,
                   specified_version=desktop_version)
hfss.modeler.model_units = length_units
hfss["H"] = "1.6mm"
hfss["L0"] = "28mm"
hfss["W0"] = "37.26mm"
hfss["L1"] = "7mm"
hfss["Length"] = "30.6mm"
# model
Box1 = hfss.modeler.create_box(["-L0", "-W0", 0], ["2*L0", "2*W0", "H"], name="Substrate", matname="FR4_epoxy")
Rectangle = hfss.modeler.create_rectangle(csPlane="XY", position=["-L0/2", "-W0/2", "H"], dimension_list=["W0", "L0"], name="Patch")
Rectangle1 = hfss.modeler.create_rectangle(csPlane="XY", position=["-L0", "-W0", "0"], dimension_list=["2*L0", "2*W0"], name="Gnd")
Cylinder = hfss.modeler.create_cylinder(cs_axis="Z", position=["L1", "0", "0"], radius=0.6, height = "H", numSides=0, name="Feed", matname="pec")
Circle = hfss.modeler.create_circle(cs_plane="XY", position=["L1", "0", "0"], radius=1.5, name="Port")
#Circle1 = hfss.modeler.create_circle(cs_plane="XY", position=["L1+0.9", "0", "0"], radius=1.5, name="Port1")
hfss.modeler.subtract(blank_list=Rectangle1, tool_list=[Circle], keep_originals=True,)

# Set boundary conditions and incentives
#PerfE1 = hfss.create_boundary("Perfect E","Patch", boundary_name="PerfE1")
#PerfE2 = hfss.create_boundary("Perfect E","Gnd", boundary_name="PerfE2")
PerfE1 = hfss.assign_perfecte_to_sheets("Patch", sourcename=None, is_infinite_gnd=False)
PerfE2 = hfss.assign_perfecte_to_sheets("Gnd", sourcename=None, is_infinite_gnd=False)



# Set radiation boundary conditions
Box2 = hfss.modeler.create_box(["-(L0/2+Length)", "-(W0/2+Length)", "-Length"], ["L0+2*Length", "W0+2*Length", "H+2*Length"], name="Airbox", matname="FR4_epoxy")
box_faces = Box2.faces
hfss.assign_radiation_boundary_to_faces(box_faces, boundary_name='Rad1')
# Set port incentives
#obj_id = hfss.modeler.get_obj_id("Port")
#face = hfss.modeler.get_face_by_id(obj_id)
#sheet_names = hfss.modeler.sheet_names("Port")

hfss.lumped_port("Port",  create_port_sheet=False, port_on_plane=True,
                 integration_line=[[7.6, 0, 0], [0.9, 0, 0]], impedance=50, name="1")






# Plot model
# ~~~~~~~~~~
# Plot the model.

my_plot = hfss.plot(show=False, plot_air_objects=False)
my_plot.show_axes = False
my_plot.show_grid = False
my_plot.isometric_view = False
my_plot.plot(
    os.path.join(hfss.working_directory, "Image.jpg"),
)





# Solve settings
setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "2.45GHz"
setup.props["MaximumPasses"] = 20
hfss.create_linear_step_sweep(
    setupname=setup.name,
    unit="GHz",
    freqstart=1.5,
    freqstop=3.5,
    step_size=0.01,
    sweepname="sweep1",
    sweep_type="Fast",
    save_fields=False,
    )

# Run simulation
hfss.analyze_setup("MySetup")


#
variations = hfss.available_variations.nominal_w_values_dict
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
variations["Freq"] = ["30GHz"]
report = hfss.post.create_report(
   "db(S(1,1)",
   hfss.nominal_adaptive,
   variations=variations,
   primary_sweep_variable="Phi",
   secondary_sweep_variable="Theta",
   plot_type="3D Polar Plot",
   context="3D",
   report_category="Far Fields",
)
'''
new_report = hfss.post.reports_by_category.far_field("db(RealizedGainTotal)", hfss.nominal_adaptive, "3D")
new_report.variations = variations
new_report.primary_sweep = "Theta"
new_report.create("Realized2D")
''
new_report.report_type = "3D Polar Plot"
new_report.secondary_sweep = "Phi"
new_report.create("Realized3D")

solution_data = new_report.get_solution_data()
solution_data.plot()

hfss.post.plot_field(
    "Realized2D",  # 
    expr="db(RealizedGainTotal)",  # 
    sweep_variable="Phi",  # 
    freq="30GHz",  # 
    context="3D",  # 
    interpoltion=False,  # 
    plottype="3D Polar Plot"  # 
)

plt.savefig('far_field_plot.png')
plt.show()
solution_data = report.get_solution_data()
solution_data.plot()

'''

