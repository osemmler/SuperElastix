import subprocess, os, logging, sys
from datetime import datetime

import SimpleITK as sitk, numpy as np

labelOverlapMeasurer = sitk.LabelOverlapMeasuresImageFilter()
labelOverlapMeasurer.SetGlobalDefaultCoordinateTolerance(1)

def merge_dicts(*dicts):
    return { key: value for dict in dicts for key, value in dict.items() }

def load_vtk(file_name):
    return np.loadtxt(file_name, skiprows=5)

def load_pts(file_name):
    return np.loadtxt(file_name)

def load_point_set(file_name):
    if file_name.endswith(".vtk"):
        return load_vtk(file_name)
    else:
        return load_pts(file_name)

def txt2vtk(point_set_file_name, displacement_field_file_name):
    # Avoid name clash by appending time in microseconds. This also makes the outputted files sortable
    output_file_name = os.path.splitext(displacement_field_file_name)[0] \
                   + '-' + "{:%Y-%m-%d-%H-%M-%S-%f}".format(datetime.now()) + '.vtk'

    try:
        point_set = np.loadtxt(point_set_file_name)
    except Exception as e:
        raise Exception('Failed to load %s: %s' % (point_set_file_name, str(e)))

    try:
        with open(output_file_name, 'w+') as f:
            f.write("# vtk DataFile Version 2.0\n")
            f.write("Point set warp generated by SuperBench\n")
            f.write("ASCII\n")
            f.write("DATASET POLYDATA\n")
            f.write("POINTS %i float\n" % point_set.shape[0])

            for point in point_set:
                for p in point:
                    f.write("%f " % p)

                f.write("\n")
    except Exception as e:
        raise Exception('Error during txt2vtk: %s' % str(e))

    return output_file_name


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def warp_point_set(superelastix, point_set_file_name, displacement_field_file_name):
    blueprint_file_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'warp_point_set.json')

    output_point_set_file_name = os.path.splitext(displacement_field_file_name)[0] + '-' \
                             + "{:%Y-%m-%d-%H-%M-%S-%f}".format(datetime.now()) + '.vtk'

    # Convert txt file to vtk format
    if not point_set_file_name.endswith(".vtk"):
        point_set_file_name = txt2vtk(point_set_file_name, displacement_field_file_name)

    try:
        stdout = subprocess.check_output([superelastix,
                                          '--conf', os.path.join(get_script_path(), 'warp_point_set.json'),
                                          '--in', 'InputPointSet=%s' % point_set_file_name,
                                          'DisplacementField=%s' % displacement_field_file_name,
                                          '--out', 'OutputPointSet=%s' % output_point_set_file_name,
                                          '--loglevel', 'trace',
                                          '--logfile', os.path.splitext(output_point_set_file_name)[0] + '.log'])
    except:
        raise Exception('\nFailed to warp %s. See %s' %
                        (point_set_file_name, os.path.splitext(output_point_set_file_name)[0] + '.log'))


    return output_point_set_file_name


def warp_label_image(superelastix, label_file_name, displacement_field_file_name):
    output_label_file_name = os.path.splitext(displacement_field_file_name)[0] + '-' \
                             + "{:%Y-%m-%d-%H-%M-%S-%f}".format(datetime.now()) + '.nii'

    try:
        stdout = subprocess.check_output([superelastix,
                                          '--conf', os.path.join(get_script_path(), 'warp_label_image.json'),
                                          '--in', 'LabelImage=%s' % label_file_name,
                                          'DisplacementField=%s' % displacement_field_file_name,
                                          '--out', 'WarpedLabelImage=%s' % output_label_file_name,
                                          '--loglevel', 'trace',
                                          '--logfile', os.path.splitext(output_label_file_name)[0] + '.log'])
    except:
        logging.error('Failed to warp %s.' % label_file_name)

    return output_label_file_name


def tre(registration_driver, point_set_file_names, deformation_field_file_names):
    point_set_0_to_1 = load_vtk(warp_point_set(registration_driver, point_set_file_names[0], deformation_field_file_names[0]))
    point_set_1_to_0 = load_vtk(warp_point_set(registration_driver, point_set_file_names[1], deformation_field_file_names[1]))
    point_set_0 = load_point_set(point_set_file_names[0])
    point_set_1 = load_point_set(point_set_file_names[1])
    return (
        { 'TRE': np.mean(np.sqrt(np.sum((point_set_0_to_1 - point_set_1) ** 2, -1))) },
        { 'TRE': np.mean(np.sqrt(np.sum((point_set_1_to_0 - point_set_0) ** 2, -1))) }
    )

def hausdorff(registration_driver, point_set_file_names, deformation_field_file_names):
    point_set_0_to_1 = load_vtk(warp_point_set(registration_driver, point_set_file_names[0], deformation_field_file_names[0]))
    point_set_1_to_0 = load_vtk(warp_point_set(registration_driver, point_set_file_names[1], deformation_field_file_names[1]))
    point_set_0 = load_point_set(point_set_file_names[0])
    point_set_1 = load_point_set(point_set_file_names[1])
    return (
        { 'Hausdorff': np.max(np.sqrt(np.sum((point_set_0_to_1 - point_set_1) ** 2, -1))) },
        { 'Hausdorff': np.max(np.sqrt(np.sum((point_set_1_to_0 - point_set_0) ** 2, -1))) }
    )

def inverse_consistency_points(registration_driver, point_set_file_names, deformation_field_file_names):
    point_set_0_to_1_file_name = warp_point_set(registration_driver, point_set_file_names[0], deformation_field_file_names[0])
    point_set_0_to_1_to_0_file_name = warp_point_set(registration_driver, point_set_0_to_1_file_name, deformation_field_file_names[1])
    point_set_1_to_0_file_name = warp_point_set(registration_driver, point_set_file_names[1], deformation_field_file_names[1])
    point_set_1_to_0_to_1_file_name = warp_point_set(registration_driver, point_set_1_to_0_file_name, deformation_field_file_names[0])
    point_set_0 = load_point_set(point_set_file_names[0])
    point_set_1 = load_point_set(point_set_file_names[1])
    return (
        { 'InverseConsistencyTRE': np.mean(np.sqrt(np.sum((load_vtk(point_set_0_to_1_to_0_file_name) - point_set_0) ** 2, -1))) },
        { 'InverseConsistencyTRE': np.mean(np.sqrt(np.sum((load_vtk(point_set_1_to_0_to_1_file_name) - point_set_1) ** 2, -1))) }
    )


def inverse_consistency_labels(registration_driver, label_file_names, deformation_field_file_names):
    label_image_0_to_1_file_name = warp_label_image(registration_driver, label_file_names[0], deformation_field_file_names[1])
    label_image_0_to_1_to_0_file_name = warp_label_image(registration_driver, label_image_0_to_1_file_name, deformation_field_file_names[0])
    label_image_1_to_0_file_name = warp_label_image(registration_driver, label_file_names[1], deformation_field_file_names[0])
    label_image_1_to_0_to_0_file_name = warp_label_image(registration_driver, label_image_1_to_0_file_name, deformation_field_file_names[1])

    try:
        label_image_0 = sitk.ReadImage(label_file_names[0])
        labelOverlapMeasurer.Execute(label_image_0, sitk.Cast(sitk.ReadImage(label_image_0_to_1_to_0_file_name), label_image_0.GetPixelID()))
        dsc_0 = labelOverlapMeasurer.GetDiceCoefficient()
    except Exception as e:
        logging.error('Failed to compute inverse consistency DSC for %s' % label_file_names[0])
        raise(e)

    try:
        label_image_1 = sitk.ReadImage(label_file_names[1])
        labelOverlapMeasurer.Execute(label_image_1, sitk.Cast(sitk.ReadImage(label_image_1_to_0_to_0_file_name), label_image_1.GetPixelID()))
        dsc_1 = labelOverlapMeasurer.GetDiceCoefficient()
    except Exception as e:
        logging.error('Failed to compute inverse consistency DSC for %s' % label_file_names[1])
        raise(e)

    return (
        {'InverseConsistencyDSC': dsc_0},
        {'InverseConsistencyDSC': dsc_1}
    )


def dice(registration_driver, label_file_names, deformation_field_file_names):
    label_image_0_to_1_file_name = warp_label_image(registration_driver, label_file_names[0], deformation_field_file_names[1])

    try:
        label_image_1 = sitk.ReadImage(label_file_names[1])
        labelOverlapMeasurer.Execute(label_image_1, sitk.Cast(sitk.ReadImage(label_image_0_to_1_file_name), label_image_1.GetPixelID()))
        dsc_0 = labelOverlapMeasurer.GetDiceCoefficient()
    except Exception as e:
        logging.error('Failed to compute DSC for %s' % label_file_names[0])
        raise(e)

    label_image_1_to_0_file_name = warp_label_image(registration_driver, label_file_names[1], deformation_field_file_names[0])

    try:
        label_image_0 = sitk.ReadImage(label_file_names[0])
        labelOverlapMeasurer.Execute(label_image_0, sitk.Cast(sitk.ReadImage(label_image_1_to_0_file_name), label_image_0.GetPixelID()))
        dsc_1 = labelOverlapMeasurer.GetDiceCoefficient()
    except Exception as e:
        logging.error('Failed to compute DSC for %s' % label_file_names[1])
        raise(e)

    return (
        {'DSC': dsc_0},
        {'DSC': dsc_1}
    )
