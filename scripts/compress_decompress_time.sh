# This needs to be changed for magistrale dataset
main=./TUMVI/magistrale/dataset-magistrale1_512_16/mav0/cam0/
directories=('video_1' 'video_5' 'video_10' 'video_15' 'video_20')
#!/bin/bash

#directories=('video')
length=${#directories[@]}
echo "$length"

for ((i=0; i<length; i++)); do
    #pwd
    echo "${directories[i]}"
    compress_time=()
    compress_size=()     
    decompress_time=()

    dir="${main}${directories[i]}/"
    cd "$dir" || continue
    output_dir="../${directories[i]}_mp4"
    decompress_dir="../${directories[i]}_uncompress"
    mkdir -p "$output_dir"
    mkdir -p "$decompress_dir"

    #counter=0

    for filepath in $(find . -maxdepth 1 -type f -name "*.yuv" | sort); do
        filename=$(basename "$filepath")      
        name="${filename%.yuv}"                
        output="$output_dir/${name}.mp4"

        # echo filepath
        #echo $filepath
        # echo $dir
        # Compression
        log_compress="$output_dir/${name}_compress.log"
        log_decompress="$decompress_dir/${name}_decompress.log"
        ffmpeg -benchmark -f rawvideo -pix_fmt yuv444p -s:v 512X512 -r 20 \
            -i "$filepath" -qp 0 -c:v libx264 "$output" -pix_fmt yuv444p -y 2>&1 | tee "$log_compress" > /dev/null
        # Compression stats
        rtime_compress=$(awk '/bench:/ && /rtime=/{match($0,/rtime=([0-9.]+)s/,a); print a[1]}' "$log_compress")
        size_compress=$(stat -c%s "$output")
        size_compress_kb=$(echo "$size_compress / 1024" | bc)
        # Uncompress
        ffmpeg -benchmark -i "$output" -f image2 -pix_fmt yuvj444p "$decompress_dir/frame_%03d.yuv" -y 2>&1 | tee "$log_decompress" > /dev/null
        rtime_decompress=$(awk '/bench:/ && /rtime=/{match($0,/rtime=([0-9.]+)s/,a); print a[1]}' "$log_decompress")

        compress_time+=(${rtime_compress})
        compress_size+=(${size_compress_kb})
        decompress_time+=(${rtime_decompress})
        
        #((counter++))
        # if [ "$counter" -eq 100 ]; then
        #     echo "Breaking loop after 10 iterations."
        #     break # Exit the loop
        # fi
        # echo "File: $filename"
        # echo "Compression Time: ${rtime_compress:-N/A} s"
        # echo "Compressed Size: ${size_compress_kb:-N/A} kB"
        # echo "Decompression Time: ${rtime_decompress:-N/A} s"
        # echo "-----------------------------"
    done

    #Average of the compression time
    sum_compress=0
    count=0
    for element in "${compress_time[@]}"; do
        sum_compress=$(awk "BEGIN {print $sum_compress + $element}")
        ((count++))
    done
    avg_compress=$(awk "BEGIN {print $sum_compress / $count}")

    # Average of the compression size
    sum_size=0
    count=0
    for element in "${compress_size[@]}"; do
        sum_size=$(awk "BEGIN {print $sum_size + $element}")
        ((count++))
    done
    avg_size=$(awk "BEGIN {print $sum_size / $count}")

    # Average time to decompress
    sum_decompress=0
    count=0
    for element in "${decompress_time[@]}"; do
        sum_decompress=$(awk "BEGIN {print $sum_decompress + $element}")
        ((count++))
    done
    avg_decompress=$(awk "BEGIN {print $sum_decompress / $count}")

    echo "Average Compression Time: ${avg_compress:-N/A} s"
    echo "Average Compressed Size: ${avg_size:-N/A} kB"
    echo "Average Decompression Time: ${avg_decompress:-N/A} s"

    cd ../../../../../..
done
