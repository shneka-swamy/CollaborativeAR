cd ORB_SLAM3

directories=(
  "results_machine_hall_adc"
  # "results_machine_hall_final"
  # "results_machine_hall_jpeg90_final"
  # "results_machine_hall_X4_UPSAMPLE"
  "results_vicon_adc"
  # "results_vicon_final"
  # "results_vicon_jpeg90_final"
  # "results_vicon_X4_UPSAMPLE"
)

# Loop through all directories
for dir in "${directories[@]}"; do
  # Find all subfolders in each directory
  for folder in "$dir"/*/; do
    [ -d "$folder" ] || continue  # skip if not a folder
    base=$(basename "$folder")
    for i in {0..4}; do
      file="${folder}CameraTrajectory_${base}__${i}_changed.csv"
        if [[ -f "$file" ]]; then
            echo "Found: $file"

            if [[ "$file" == *"machine_hall"* ]]; then
                # e.g., MH01 → MH_01
                new_base=$(echo "$base" | sed -E 's/MH([0-9]{2})/MH_\1/')
                
                out_file="${folder}ARE_${base}_${i}.txt"
                [ -f "$out_file" ] && rm "$out_file"
                evo_ape euroc -as ../EuRoC/machine_hall/"$new_base"/mav0/state_groundtruth_estimate0/data.csv "$file" --pose_relation angle_rad >> "$out_file"

            elif [[ "$file" == *"V1"* || "$file" == *"V2"* ]]; then
                # e.g., V101 → V1_01, V201 → V2_01
                new_base=$(echo "$base" | sed -E 's/(V[0-9])([0-9]{2})/\1_\2/')
                
                out_file="${folder}ARE_${base}_${i}.txt"
                evo_ape euroc -as ../EuRoC/vicon/"$new_base"/mav0/state_groundtruth_estimate0/data.csv "$file" --pose_relation angle_rad >> "$out_file"
            fi
        else
            echo "Unknown dataset type for $file"
        fi
    done
  done
done
