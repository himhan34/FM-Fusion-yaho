import os,glob 
import numpy as np
import open3d as o3d
from operator import itemgetter

COLOR20 = np.array(
        [[230, 25, 75], [60, 180, 75], [255, 225, 25], [0, 130, 200], [245, 130, 48],
        [145, 30, 180], [70, 240, 240], [240, 50, 230], [210, 245, 60], [250, 190, 190],
        [0, 128, 128], [230, 190, 255], [170, 110, 40], [255, 250, 200], [128, 0, 0],
        [170, 255, 195], [128, 128, 0], [255, 215, 180], [0, 0, 128], [128, 128, 128]])

SEMANTIC_IDXS = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 24, 28, 33, 34, 36, 39])
SEMANTIC_NAMES = np.array(['wall', 'floor', 'cabinet', 'bed', 'chair', 'sofa', 'table', 'door', 'window', 'bookshelf', 'picture', 'counter',
                        'desk', 'curtain', 'refridgerator', 'shower curtain', 'toilet', 'sink', 'bathtub', 'otherfurniture'])

CLASS_COLOR = {
    'unannotated': [0, 0, 0],
    'floor': [143, 223, 142],
    'wall': [171, 198, 230],
    'cabinet': [0, 120, 177],
    'bed': [255, 188, 126],
    'chair': [189, 189, 57],
    'sofa': [144, 86, 76],
    'table': [255, 152, 153],
    'door': [222, 40, 47],
    'window': [197, 176, 212],
    'bookshelf': [150, 103, 185],
    'picture': [200, 156, 149],
    'counter': [0, 190, 206],
    'desk': [252, 183, 210],
    'curtain': [219, 219, 146],
    'refridgerator': [255, 127, 43],
    'bathtub': [234, 119, 192],
    'shower curtain': [150, 218, 228],
    'toilet': [0, 160, 55],
    'sink': [110, 128, 143],
    'otherfurniture': [80, 83, 160]
}


def get_coords_color(task,result_dir):    
    composite_labels = np.load(result_dir).astype(np.int32)
    sem_pred = np.floor(composite_labels / 1000)
    sem_pred = sem_pred.astype(np.int32)
    instances = composite_labels - sem_pred * 1000
    N = sem_pred.shape[0]

    if task=='semantic_pred':
        # print(sem_pred.max())
        valid = (sem_pred>=0) & (sem_pred<20)
        # sem_pred = 5 * np.ones((N)).astype(np.int32)
        rgb = np.zeros((N,3)).astype(np.uint8)
        rgb[valid] = np.array(itemgetter(*SEMANTIC_NAMES[sem_pred[valid]])(CLASS_COLOR))

    elif task=='instance_pred':
        # instance_file = os.path.join(opt.result_root, opt.room_split, scan + '.txt')
        # assert os.path.isfile(instance_file), 'No instance result - {}.'.format(instance_file)
        # f = open(instance_file, 'r')
        # masks = f.readlines()
        # masks = [mask.rstrip().split() for mask in masks]
        inst_label_pred_rgb = np.zeros((N,3)).astype(np.int32)  # np.ones(rgb.shape) * 255 #
        instance_list = np.unique(instances)

        # print('instnace list: {}'.format(instance_list))
        
        for idx in instance_list[:-1]:
            # mask_path = os.path.join(opt.result_root, opt.room_split, masks[i][0])
            # assert os.path.isfile(mask_path), mask_path
            # if (float(masks[i][2]) < 0.09):
            #     continue
            # mask = np.loadtxt(mask_path).astype(np.int32)
            # print('{} {}: {} pointnum: {}'.format(i, masks[i], SEMANTIC_IDX2NAME[int(masks[i][1])], mask.sum()))
            
            
            inst_label_pred_rgb[instances == idx] = COLOR20[idx % len(COLOR20)]
        rgb = inst_label_pred_rgb

    return rgb, sem_pred, instances

def generate_colors(composite_labels):
    
    sem_pred = np.floor(composite_labels / 1000)
    sem_pred = sem_pred.astype(np.int32)
    instances = composite_labels - sem_pred * 1000
    N = sem_pred.shape[0]
    
    # Semantic color
    valid = (sem_pred>=0) & (sem_pred<20)
    semantic_colors = np.zeros((N,3)).astype(np.uint8)
    semantic_colors[valid] = np.array(itemgetter(*SEMANTIC_NAMES[sem_pred[valid]])(CLASS_COLOR))

    # Instance color
    instance_colors = np.zeros((N,3)).astype(np.int32)
    instance_list = np.unique(instances)
    for idx in instance_list[:-1]:
        instance_colors[instances == idx] = COLOR20[idx % len(COLOR20)]

    return semantic_colors, instance_colors

# todo
def create_instance_centroid(points, instances, labels):
    instance_idxs = np.unique(instances)
    centroid_spheres = []
    for id in instance_idxs:
        instance_points = points[instances==id]
        centroid = np.mean(instance_points,axis=0)
        mesh_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
        label_name = SEMANTIC_NAMES[labels[instances==id][0]]
        label_color = CLASS_COLOR[label_name]
        # mesh_sphere.compute_vertex_normals()
        mesh_sphere.paint_uniform_color([label_color[0] / 255.0,label_color[1]/255.0,label_color[2]/255.0]) # ([0.1, 0.1, 0.7])
        centroid_spheres.append(mesh_sphere.translate(centroid))
    return centroid_spheres

def read_scans(dir):
    with open(dir,'r') as f:
        lines = f.readlines()
        scans =[]
        for line in lines:
            scans.append(line.strip())
        f.close()
        return scans

if __name__=='__main__':
    
    dataroot = '/data2/ScanNet'
    split = 'val'
    test_set = 'filtertag_proposed' 
    # test_set = 'fusion++'

    eval_dir = '/data2/ScanNet/eval'
    save_map_dir = None  
    save_map_dir = os.path.join('/data2/ScanNet/output',test_set)
    os.environ.setdefault('WEBRTC_IP', '143.89.46.75')
    os.environ.setdefault('WEBRTC_PORT', '8020')
    scans = read_scans(os.path.join(dataroot,'splits','val_clean.txt'))
    valid_scans = [scan for scan in scans if os.path.exists(os.path.join(eval_dir,test_set,scan,'result.npy'))]
    
    print('find {} scans'.format(len(valid_scans)))
    # RENDER_TYPE='semantic_pred'
    # RENDER_TYPE='instance_pred'
    # scans = ['scene0064_00']

    for scan in valid_scans:
        scan_dir = os.path.join(dataroot,split,scan)
        result_dir = os.path.join(eval_dir,test_set,scan,'result.npy')

        scene_name = os.path.basename(scan_dir)
        map_dir = os.path.join(scan_dir,'{}_{}'.format(scene_name,'vh_clean_2.ply'))
        pcd_semantic = o3d.io.read_point_cloud(map_dir)
        pcd_instance = o3d.io.read_point_cloud(map_dir)
        
        rgb, _, _ = get_coords_color('semantic_pred',result_dir)
        pcd_semantic.colors = o3d.utility.Vector3dVector(rgb/255.0)
        rgb, _, _ = get_coords_color('instance_pred',result_dir)
        pcd_instance.colors = o3d.utility.Vector3dVector(rgb/255.0)
        pcd_instance = pcd_instance.translate([0,10,0])

        out = [pcd_semantic]
        # print(pcd_semantic)
        
        
        # break
        if save_map_dir is not None:
            if os.path.exists(save_map_dir) is False:
                os.makedirs(save_map_dir)
            o3d.io.write_point_cloud(os.path.join(save_map_dir,'{}_semantic.ply'.format(scan)),pcd_semantic)
            o3d.io.write_point_cloud(os.path.join(save_map_dir,'{}_instance.ply'.format(scan)),pcd_instance)
        else:        
            o3d.visualization.webrtc_server.enable_webrtc()
            o3d.visualization.draw(out)