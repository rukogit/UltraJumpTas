import os, sys, glob, copy

import gspread
from dataclasses import dataclass
from util import ChapterTime, format_frames

@dataclass
class Color:
    red: float
    green: float
    blue: float

sheet_name = "Ultra Jump TAS - Statistics"
anypercent_name = "any%"
trueending_name = "All A-Sides / True Ending"
il_worksheet = "testing 1"

gc: gspread.client.Client = None
if "GITHUB_WORKFLOW" in os.environ:
    credentials = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_AUTH_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_AUTH_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_AUTH_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_AUTH_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_AUTH_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ultrajump-github-workflow%40python-spreadsheets-402713.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }
    gc = gspread.service_account_from_dict(credentials)
else:
    gc = gspread.oauth()

sh = gc.open(sheet_name)

color_white = Color(1.0, 1.0, 1.0)
color_black = Color(0.0, 0.0, 0.0)
color_green = Color(0.0, 1.0, 0.0)
color_red   = Color(1.0, 0.0, 0.0)

all_times: dict[str, ChapterTime] = {}

def fill_out_time(updates, column, row, column_files):
    for i, file in enumerate(column_files):
        text = "[Not drafted]"
        if file in all_times:
            text = str(all_times[file])

        cell = f"{column}{row + i}"
        updates.append(gspread.cell.Cell.from_address(cell, text))

def fill_out_diff(updates, formats, files, column, row, column_files, base_files):
    for i, file in enumerate(column_files):
        text = "-"
        color = color_black
        if file in files and base_files[i] in files:
            frames = files[file]["time"].frames - files[base_files[i]]["time"].frames
            text = format_frames(frames)
            if frames < 0:
                color = color_green
            else:
                color = color_red

        cell = f"{column}{row + i}"
        updates.append(gspread.cell.Cell.from_address(cell, text))
        formats.append({
            "range": cell,
            "format": {"textFormat": {"foregroundColor": color}}
        })

def update_il():
    chapters = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    # Update spreadsheet
    sheet = sh.worksheet(il_worksheet)
    updates = []
    formats = []

    a_files = ["1A.tas", "2A.tas", "3A.tas", "4A.tas", "5A.tas", "6A.tas", "7A.tas", "8A.tas", "9.tas" ]
    b_files = ["1B.tas", "2B.tas", "3B.tas", "4B.tas", "5B.tas", "6B.tas", "7B.tas", "8B.tas" ]
    c_files = ["1C.tas", "2C.tas", "3C.tas", "4C.tas", "5C.tas", "6C.tas", "7C.tas", "8C.tas" ]
    h_files = ["1H.tas", "2H.tas", "3H.tas", "4H.tas", "5H.tas", "6H.tas", "7H.tas", "8H.tas" ]
    ac_files = ["1AC.tas", "2AC.tas", "3AC.tas", "4AC.tas", "5AC.tas", "6AC.tas", "7AC.tas", "8AC.tas" ]
    s_files = ["1S.tas", "2S.tas", "3S.tas", "4S.tas", "5S.tas", "6S.tas", "7S.tas", "8S.tas", "9S.tas" ]
    hc_files = ["1HC.tas", "2HC.tas", "3HC.tas", "4HC.tas", "5HC.tas", "6HC.tas", "7HC.tas", "8HC.tas" ]
    sh_files = ["1SH.tas", "2SH.tas", "3SH.tas", "4SH.tas", "5SH.tas", "6SH.tas", "7SH.tas", "8SH.tas" ]
    shc_files = ["1SHC.tas", "2SHC.tas", "3SHC.tas", "4SHC.tas", "5SHC.tas", "6SHC.tas", "7SHC.tas", "8SHC.tas" ]
    
    fill_out_time(updates, "C", 6, a_files)
    fill_out_time(updates, "D", 6, b_files)
    fill_out_time(updates, "E", 6, c_files)
    
    fill_out_time(updates, "C", 17, h_files)
    fill_out_time(updates, "D", 17, ac_files)
    fill_out_time(updates, "E", 17, s_files)
    fill_out_time(updates, "F", 17, hc_files)
    fill_out_time(updates, "G", 17, sh_files)
    fill_out_time(updates, "H", 17, shc_files)

    sheet.update_cells(updates)
    
def update_anypercent():
    chapters = ["1", "2", "3", "4", "5", "6", "7"]
    times = copy.deepcopy(all_times)

    # Merge B into AC
    for c in chapters:
        b = f"{c}B.tas"
        ac = f"{c}AC.tas"
        if not b in times or not ac in times:
            continue
        times[ac] = ChapterTime.from_frames(times[ac].frames + times[b].frames)

    # Update spreadsheet
    sheet = sh.worksheet(anypercent_name)
    updates = []
    formats = []

    a_files = ["1A.tas", "2A.tas", "3A.tas", "4A.tas", "5A.tas", "6A.tas", "7A.tas" ]
    ac_files = ["1AC.tas", "2AC.tas", "3AC.tas", "4AC.tas", "5AC.tas", "6AC.tas", "7AC.tas" ]
    b_files = ["1B.tas", "2B.tas", "3B.tas", "4B.tas", "5B.tas", "6B.tas", "7B.tas" ]
    fill_out_time(updates, formats, files, "B", a_files)
    fill_out_time(updates, formats, files, "C", ac_files)
    fill_out_time(updates, formats, files, "E", b_files)
    fill_out_diff(updates, formats, files, "D", ac_files, a_files)

    # sheet.update_cells(updates)
    # sheet.batch_format(formats)

def update_trueending():
    chapters = ["1", "2", "3", "4", "5", "6", "7"]
    files = copy.deepcopy(all_times)


    # Merge B-Side into AC/HC
    for f in all_times:
        if not f.endswith("B.tas"):
            continue
        ac = f"{f[0]}AC.tas"
        hc = f"{f[0]}HC.tas"
        if not f in files:
            continue
        if ac in files:
          files[ac]["time"] = ChapterTime.from_frames(files[ac]["time"].frames + files[f]["time"].frames)
        if hc in files:
          files[hc]["time"] = ChapterTime.from_frames(files[hc]["time"].frames + files[f]["time"].frames)

    # # Select faster version by color
    # for c in chapters:
    #     a = f"{c}A.tas"
    #     ac = f"{c}AC.tas"
    #     b = f"{c}B.tas"
    #     if not a in files and not ac in files:
    #         continue # Nothing drafted
    #     elif a in files and not ac in files:
    #         files[a]["color"] = color_green # Only A-Side Drafted
    #     elif not a in files and ac in files:
    #         files[ac]["color"] = color_green # Only B-Side Drafted    
    #     elif a in files and ac in files:
    #         a_frames = files[a]["time"].frames
    #         ac_frames = files[ac]["time"].frames
    #         if a_frames < ac_frames:
    #             files[a]["color"] = color_green
    #         elif ac_frames < a_frames:
    #             files[ac]["color"] = color_green
    #         else:
    #             files[a]["color"] = color_green
    #             files[ac]["color"] = color_green
    #     # Mark B-Side red if slower than A-Side alone
    #     if not a in files or not b in files:
    #         continue
    #     a_frames = files[a]["time"].frames
    #     b_frames = files[b]["time"].frames
    #     if b_frames > a_frames:
    #         files[b]["color"] = color_red

    # Update spreadsheet
    sheet = sh.worksheet(trueending_name)

    updates = []
    formats = []
    fill_out_time(updates, formats, files, "B", a_files)
    fill_out_time(updates, formats, files, "C", h_files)
    fill_out_time(updates, formats, files, "E", ac_files)
    fill_out_time(updates, formats, files, "G", hc_files)

    fill_out_diff(updates, formats, files, "D", h_files, a_files)
    fill_out_diff(updates, formats, files, "F", ac_files, a_files)
    fill_out_diff(updates, formats, files, "H", hc_files, a_files)

    sheet.update_cells(updates)
    sheet.batch_format(formats)

if __name__ == "__main__":
    # Fetch all files
    for path in glob.glob(os.path.join(sys.argv[1], "*.tas")):
        try:
            filename = os.path.basename(path)
            print(f"Getting time for {filename}...", end="")
            time = None
            with open(path, "r") as f:
                lines = reversed(list(f))
                for line in lines:
                    time = ChapterTime.parse(line)
                    if time is not None:
                        break
            if time is None:
                print(" ChapterTime missing")
                continue

            all_times[filename] = time
            
            print(f" Success ({time})")
        except Exception as ex:
            print(" Not found")
            print(ex)
            pass

    # update_anypercent()
    # update_trueending()
    update_il()
