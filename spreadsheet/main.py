import os, sys, glob, copy
import gspread
from util import ChapterTime, format_frames

sheet_name = "Ultra Jump TAS - Statistics"
anypercent_name = "any%"
trueending_name = "All A-Sides / True Ending"

gc = None
if os.getenv("GITHUB_WORKFLOW") == "YES":
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

color_white = { "red": 1.0, "green": 1.0, "blue": 1.0 }
color_black = { "red": 0.0, "green": 0.0, "blue": 0.0 }
color_green = { "red": 0.0, "green": 1.0, "blue": 0.0 }
color_red   = { "red": 1.0, "green": 0.0, "blue": 0.0 }

all_files = {}

def fill_out_time(updates, formats, files, column, column_files):
    for i, file in enumerate(column_files):
        text = "-"
        color = color_white
        if file in files:
            text = str(files[file]["time"])
            color = files[file]["color"]

        cell = f"{column}{2 + i}"
        updates.append(gspread.cell.Cell.from_address(cell, text))
        # formats.append({
        #     "range": cell,
        #     "format": {"backgroundColor": color}
        # })

def fill_out_diff(updates, formats, files, column, column_files, base_files):
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

        cell = f"{column}{2 + i}"
        updates.append(gspread.cell.Cell.from_address(cell, text))
        formats.append({
            "range": cell,
            "format": {"textFormat": {"foregroundColor": color}}
        })


def update_anypercent():
    chapters = ["1", "2", "3", "4", "5", "6", "7"]
    a_files = ["1A.tas", "2A.tas", "3A.tas", "4A.tas", "5A.tas", "6A.tas", "7A.tas" ]
    ac_files = ["1AC.tas", "2AC.tas", "3AC.tas", "4AC.tas", "5AC.tas", "6AC.tas", "7AC.tas" ]
    b_files = ["1B.tas", "2B.tas", "3B.tas", "4B.tas", "5B.tas", "6B.tas", "7B.tas" ]
    files = copy.deepcopy(all_files)

    # Merge B-Side into AC
    for f in b_files:
        if not f.endswith("B.tas"):
            continue
        ac = f"{f[0]}AC.tas"
        if not f in files or not ac in files:
            continue
        files[ac]["time"] = ChapterTime.from_frames(files[ac]["time"].frames + files[f]["time"].frames)

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
    sheet = sh.worksheet(anypercent_name)
    updates = []
    formats = []

    fill_out_time(updates, formats, files, "B", a_files)
    fill_out_time(updates, formats, files, "C", ac_files)
    fill_out_time(updates, formats, files, "E", b_files)
    fill_out_diff(updates, formats, files, "D", ac_files, a_files)

    sheet.update_cells(updates)
    sheet.batch_format(formats)

def update_trueending():
    chapters = ["1", "2", "3", "4", "5", "6", "7"]
    a_files = ["1A.tas", "2A.tas", "3A.tas", "4A.tas", "5A.tas", "6A.tas", "7A.tas" ]
    h_files = ["1H.tas", "2H.tas", "3H.tas", "4H.tas", "5H.tas", "6H.tas", "7H.tas" ]
    hc_files = ["1HC.tas", "2HC.tas", "3HC.tas", "4HC.tas", "5HC.tas", "6HC.tas", "7HC.tas" ]
    ac_files = ["1AC.tas", "2AC.tas", "3AC.tas", "4AC.tas", "5AC.tas", "6AC.tas", "7AC.tas" ]
    b_files = ["1B.tas", "2B.tas", "3B.tas", "4B.tas", "5B.tas", "6B.tas", "7B.tas" ]
    files = copy.deepcopy(all_files)


    # Merge B-Side into AC/HC
    for f in all_files:
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

            all_files[filename] = { "time": time, "color": color_white }
            
            print(f" Success ({time})")
        except Exception as ex:
            print(" Not found")
            print(ex)
            pass

    update_anypercent()
    update_trueending()
