#include <iostream>
#include <memory>
#include <vector>
#include <fstream>

#include "open3d/Open3D.h"
#include "opencv2/opencv.hpp"

#include "Utility.h"
#include "SceneGraph.h"
#include "Common.h"

using namespace open3d::visualization;


int main(int argc, char *argv[]) 
{
    using namespace open3d;

    std::string config_file = utility::GetProgramOptionAsString(argc, argv, "--config");
    std::string map_folder = utility::GetProgramOptionAsString(argc, argv, "--map_folder");
    std::string src_sequence = utility::GetProgramOptionAsString(argc, argv, "--scene_name");
    bool visualization = utility::ProgramOptionExists(argc, argv, "--visualization");


    // init
    auto sg_config = fmfusion::utility::create_scene_graph_config(config_file, true);
    if(sg_config==nullptr) {
        utility::LogWarning("Failed to create scene graph config.");
        return 0;
    }
    auto global_scene_graph = std::make_shared<fmfusion::SceneGraph>(fmfusion::SceneGraph(*sg_config));

    // Pose Graph
    auto pose_graph_io = std::make_shared<fmfusion::PoseGraphFile>();
    if(open3d::io::ReadIJsonConvertible(map_folder+"/"+src_sequence+"/pose_map.json", *pose_graph_io)){
        fmfusion::o3d_utility::LogInfo("Read pose graph from {}.",src_sequence);
    }
    auto pose_map = pose_graph_io->poses_;

    //
    int count=0;
    for (auto it=pose_map.begin();it!=pose_map.end();it++){
        fmfusion::o3d_utility::LogInfo("Scene: {}",it->first);
        std::string scene_folder = map_folder+"/"+it->first;

        global_scene_graph->load(scene_folder);
        if count>0:
            global_scene_graph->merge_overlap_instances();

        count ++;
        break;

    }
    global_scene_graph->extract_bounding_boxes();

    //
    if (visualization){
        auto geometries = scene_graph.get_geometries(true,true);
        open3d::visualization::DrawGeometries(geometries, sequence_name+subseq, 1920, 1080);
    }
    


    return 0;

}