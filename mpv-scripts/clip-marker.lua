-- ClipJits MPV Script for marking and creating video clips
-- Keybindings: s (start), e (end), c (commit)

local utils = require 'mp.utils'
local msg = require 'mp.msg'

local clip_start = nil
local clip_end = nil
local clips_dir = nil

function get_clips_dir()
    if clips_dir then
        return clips_dir
    end
    
    local script_opts = mp.get_property_native("script-opts")
    if script_opts and script_opts["clipjits-clips-dir"] then
        clips_dir = script_opts["clipjits-clips-dir"]
        return clips_dir
    end
    
    -- Default fallback
    clips_dir = "./jits/clips"
    return clips_dir
end

function to_snake_case(text)
    -- Convert to lowercase
    text = string.lower(text)
    -- Replace spaces and hyphens with underscores
    text = string.gsub(text, "[%s%-]+", "_")
    -- Remove special characters
    text = string.gsub(text, "[^%w_]", "")
    -- Remove multiple underscores
    text = string.gsub(text, "_+", "_")
    -- Trim underscores from start and end
    text = string.gsub(text, "^_+", "")
    text = string.gsub(text, "_+$", "")
    -- Truncate to 50 characters
    if string.len(text) > 50 then
        text = string.sub(text, 1, 50)
        text = string.gsub(text, "_+$", "")
    end
    return text
end

function format_timestamp(seconds)
    if not seconds then return "00:00:00.000" end
    local hours = math.floor(seconds / 3600)
    local minutes = math.floor((seconds % 3600) / 60)
    local secs = seconds % 60
    return string.format("%02d:%02d:%06.3f", hours, minutes, secs)
end

function extract_clip(source_video, start_time, end_time, label)
    local dir = get_clips_dir()
    
    -- Ensure directory exists
    if package.config:sub(1,1) == '\\' then
        os.execute('if not exist "' .. dir .. '" mkdir "' .. dir .. '"')
    else
        os.execute('mkdir -p "' .. dir .. '"')
    end
    
    -- Get source video filename without extension
    local source_name = source_video:match("([^/\\]+)$")
    source_name = source_name:match("(.+)%..+$") or source_name
    source_name = to_snake_case(source_name)
    
    label = to_snake_case(label)
    
    local output_filename = source_name .. "_" .. label .. ".mp4"
    local output_path = dir .. "/" .. output_filename
    
    -- Calculate duration
    local start_seconds = parse_timestamp(start_time)
    local end_seconds = parse_timestamp(end_time)
    local duration = end_seconds - start_seconds
    
    -- Build ffmpeg command (suppress output)
    local cmd
    if package.config:sub(1,1) == '\\' then
        -- Windows
        cmd = string.format(
            'ffmpeg -y -ss %f -i "%s" -t %f -c:v libx264 -c:a aac -avoid_negative_ts make_zero "%s" >nul 2>&1',
            start_seconds, source_video, duration, output_path
        )
    else
        -- Unix
        cmd = string.format(
            "ffmpeg -y -ss %f -i '%s' -t %f -c:v libx264 -c:a aac -avoid_negative_ts make_zero '%s' >/dev/null 2>&1",
            start_seconds, source_video, duration, output_path
        )
    end
    
    mp.osd_message("Extracting clip...", 2)
    
    local result = os.execute(cmd)
    
    if result == 0 or result == true then
        mp.osd_message("✓ Clip saved: " .. output_filename, 3)
        print("[ClipJits] ✓ Clip saved: " .. output_filename)
        return true
    else
        mp.osd_message("✗ Extraction failed", 3)
        print("[ClipJits] ✗ FATAL ERROR: Extraction failed for " .. output_filename)
        return false
    end
end

function parse_timestamp(timestamp)
    local hours, minutes, seconds = timestamp:match("(%d+):(%d+):([%d.]+)")
    if hours then
        return tonumber(hours) * 3600 + tonumber(minutes) * 60 + tonumber(seconds)
    end
    
    minutes, seconds = timestamp:match("(%d+):([%d.]+)")
    if minutes then
        return tonumber(minutes) * 60 + tonumber(seconds)
    end
    
    return tonumber(timestamp) or 0
end

function mark_start()
    clip_start = mp.get_property_number("time-pos")
    if clip_start then
        mp.osd_message(string.format("✓ Start: %s", format_timestamp(clip_start)), 2)
        print(string.format("[ClipJits] Start marked: %s", format_timestamp(clip_start)))
    end
end

function mark_end()
    clip_end = mp.get_property_number("time-pos")
    if clip_end then
        mp.osd_message(string.format("✓ End: %s", format_timestamp(clip_end)), 2)
        print(string.format("[ClipJits] End marked: %s", format_timestamp(clip_end)))
    end
end

function commit_clip()
    if not clip_start then
        mp.osd_message("Error: No start time marked (press 's' first)", 3)
        return
    end
    
    if not clip_end then
        mp.osd_message("Error: No end time marked (press 'e' first)", 3)
        return
    end
    
    if clip_end <= clip_start then
        mp.osd_message("Error: End time must be after start time", 3)
        return
    end
    
    local video_path = mp.get_property("path")
    if not video_path then
        mp.osd_message("Error: No video loaded", 3)
        return
    end
    
    local was_paused = mp.get_property_bool("pause")
    mp.set_property("pause", "yes")
    
    mp.osd_message("Enter label in terminal (required)", 3)
    
    print("\n" .. string.rep("─", 50))
    io.write("Enter clip label (required): ")
    io.flush()
    local label = io.read()
    print(string.rep("─", 50))
    
    -- Label is now required
    if not label or label == "" then
        mp.osd_message("Error: Label is required", 3)
        print("[ClipJits] Error: Label cannot be empty\n")
        if not was_paused then
            mp.set_property("pause", "no")
        end
        return
    end
    
    local start_formatted = format_timestamp(clip_start)
    local end_formatted = format_timestamp(clip_end)
    
    -- Extract clip immediately
    if extract_clip(video_path, start_formatted, end_formatted, label) then
        clip_start = nil
        clip_end = nil
    end
    
    if not was_paused then
        mp.set_property("pause", "no")
    end
end

math.randomseed(os.time())

mp.add_key_binding("s", "mark_clip_start", mark_start)
mp.add_key_binding("e", "mark_clip_end", mark_end)
mp.add_key_binding("c", "commit_clip", commit_clip)

mp.osd_message("ClipJits ready: s=start, e=end, c=commit", 3)
print("[ClipJits] Ready. Press 's' to mark start, 'e' to mark end, 'c' to commit.")
