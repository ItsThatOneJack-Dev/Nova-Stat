import rich, sys, requests, json
from rich import print
from rich.prompt import Prompt
from rich.table import Table

def GetIDByName(Username):
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [Username],"excludeBannedUsers": False}
    headers = {"Content-Type": "application/json","accept": "application/json"}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data["data"] and len(data["data"]) > 0:
            return data["data"][0]["id"]
        else:
            print(f"No user found with username: {Username}")
            return None
    else:
        print(f"Error: HTTP-ID-{response.status_code}")
        return None


def GetGroupsInfo(UserID):
    url = f"https://groups.roblox.com/v2/users/{UserID}/groups/roles"
    params = {"includeLocked": "true","includeNotificationPreferences": "false"}
    headers = {"accept": "application/json"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: HTTP-GROUP-{response.status_code}")
        return None

def ParseGroupsInfo(GroupsInfo):
    result = {"Clearance": None,"ClearanceID": None,"Departments": []}
    department_group_ids = [5508925, 4971982, 4971979, 4971978, 4971973]
    nova_group_id = 4965800
    department_info = {}
    
    for group_info in GroupsInfo["data"]:
        group_id = group_info["group"]["id"]
        
        if group_id == nova_group_id:
            result["Clearance"] = group_info["role"]["name"]
            result["ClearanceID"] = group_info["role"]["rank"]
        
        if group_id in department_group_ids:
            department_info[group_id] = {
                "Department": group_info["group"]["name"].replace("[:] ", ""),
                "Rank": group_info["role"]["name"],
                "RankID": group_info["role"]["rank"]
            }

    for dept_id in department_group_ids:
        if dept_id in department_info:
            result["Departments"].append(department_info[dept_id])
    return result

if __name__ == "__main__":
    Username = Prompt.ask("Username of user: ", default="StrayDev14")
    UserID = GetIDByName(Username)
    if UserID:
        GroupsInfo = GetGroupsInfo(UserID)
        if GroupsInfo:
            Result = ParseGroupsInfo(GroupsInfo)
            OwnershipSuffix = "'s" if Username.lower()[-1]!="s" else "'"
            print("")
            print(f"[italic purple]{Username}{OwnershipSuffix}[/italic purple] Statistics")
            print("")
            print(f"[italic blue] Clearance: [/italic blue]{Result['Clearance']} (ID: {Result['ClearanceID']})")
            print("")
            if Result["Departments"]:
                table = Table(show_header=True, header_style="bold italic blue", box=None)
                table.add_column("Department", style="green")
                table.add_column("Rank", style="green")
                for dept in Result["Departments"]:
                    table.add_row(dept["Department"],f"{dept['Rank']} (ID: [cyan]{dept['RankID']}[/cyan])")
                print(table)
            else:
                print("[italic yellow]No departments found from the specified list.[/italic yellow]")
        else:
            print(f"[bold red]Could not retrieve group information for {Username}[/bold red]")
    else:
        print(f"[bold red]Could not retrieve user ID for {Username}[/bold red]")
