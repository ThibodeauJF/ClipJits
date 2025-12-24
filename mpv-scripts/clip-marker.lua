-- ClipJits MPV Script for marking and creating video clips
-- Keybindings: s (start), e (end), c (commit)

local utils = require 'mp.utils'
local msg = require 'mp.msg'

local clip_start = nil
local clip_end = nil
local queue_file = nil

function get_queue_file()
    if queue_file then
        return queue_file
    end
    
    local script_opts = mp.get_property_native("script-opts")
    if script_opts and script_opts["clipjits-queue-file"] then
        queue_file = script_opts["clipjits-queue-file"]
        return queue_file
    end
    
    local home = os.getenv("HOME") or os.getenv("USERPROFILE")
    queue_file = home .. "/.clipjits/clip_queue.json"
    return queue_file
end

function format_timestamp(seconds)
    if not seconds then return "00:00:00.000" end
    local hours = math.floor(seconds / 3600)
    local minutes = math.floor((seconds % 3600) / 60)
    local secs = seconds % 60
    return string.format("%02d:%02d:%06.3f", hours, minutes, secs)
end

function load_queue()
    local file_path = get_queue_file()
    local file = io.open(file_path, "r")
    
    if not file then
        return {clips = {}}
    end
    
    local content = file:read("*all")
    file:close()
    
    if content == "" then
        return {clips = {}}
    end
    
    local success, queue_data = pcall(utils.parse_json, content)
    if success and queue_data then
        return queue_data
    else
        return {clips = {}}
    end
end

function save_queue(queue_data)
    local file_path = get_queue_file()
    
    local dir = file_path:match("(.*/)")
    if dir then
        os.execute("mkdir -p " .. dir)
    end
    
    local file = io.open(file_path, "w")
    if not file then
        mp.osd_message("Error: Cannot write to queue file", 3)
        return false
    end
    
    local json_str = utils.format_json(queue_data)
    file:write(json_str)
    file:close()
    
    return true
end

function generate_uuid()
    local template = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    return string.gsub(template, '[xy]', function(c)
        local v = (c == 'x') and math.random(0, 0xf) or math.random(8, 0xb)
        return string.format('%x', v)
    end)
end

function mark_start()
    clip_start = mp.get_property_number("time-pos")
    if clip_start then
        mp.osd_message(string.format("Clip start marked: %s", format_timestamp(clip_start)), 2)
        msg.info("Clip start marked at: " .. clip_start)
    end
end

function mark_end()
    clip_end = mp.get_property_number("time-pos")
    if clip_end then
        mp.osd_message(string.format("Clip end marked: %s", format_timestamp(clip_end)), 2)
        msg.info("Clip end marked at: " .. clip_end)
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
    
    mp.osd_message("Enter label (leave empty for auto): ", 30)
    
    local label_input = mp.command_native({
        name = "input",
        prompt = "Clip label:",
        default_text = "",
    })
    
    local label = ""
    if label_input and label_input ~= "" then
        label = label_input
    end
    
    local queue_data = load_queue()
    
    local new_clip = {
        id = generate_uuid(),
        source_video = video_path,
        start_time = format_timestamp(clip_start),
        end_time = format_timestamp(clip_end),
        label = label,
        created_at = os.date("!%Y-%m-%dT%H:%M:%S")
    }
    
    table.insert(queue_data.clips, new_clip)
    
    if save_queue(queue_data) then
        local msg_text = string.format(
            "Clip added to queue\nLabel: %s\nStart: %s\nEnd: %s",
            label ~= "" and label or "(none)",
            format_timestamp(clip_start),
            format_timestamp(clip_end)
        )
        mp.osd_message(msg_text, 4)
        msg.info("Clip committed: " .. new_clip.id)
        
        clip_start = nil
        clip_end = nil
    end
end

math.randomseed(os.time())

mp.add_key_binding("s", "mark_clip_start", mark_start)
mp.add_key_binding("e", "mark_clip_end", mark_end)
mp.add_key_binding("c", "commit_clip", commit_clip)

mp.osd_message("ClipJits loaded - s:start e:end c:commit", 3)
msg.info("ClipJits script loaded successfully")
