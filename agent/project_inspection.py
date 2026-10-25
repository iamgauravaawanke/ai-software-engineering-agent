from pathlib import Path
import re

def validate_project_path(project_path:str):

    # Step 1: Convert the path into a Path object

    project_path_obj = Path(project_path)
    
    # Step 2: Check whether the path exists
    if not project_path_obj.exists():
            
        return {
                    "valid":False,
                    "error": "PROJECT_PATH_NOT_FOUND"
                }
                
            # Step 3: Check whether the path is a directory

    if not project_path_obj.is_dir():
        return{
                    "valid":False,
                    "error": "NOT_A_DIRECTORY",
                }
                
            # Step 4: All checks passed
    return{
                "valid":True,
                "error":None
            }   

def list_project_items(project_path: str):
    
    validation_result = validate_project_path(project_path)
    
    if not validation_result["valid"]:
        return validation_result
    
    paths_object  = Path(project_path)
    
    
    excluded_dirs = {".git", ".venv", "venv"}
    list_items = []
    
    #  Inspect directories recursively
    def insepect_directiory(current_directiory :Path):
        
    
        for item in current_directiory.iterdir():
            # print("item" , item)
            
            #Skip excluded directories completely
            
            if item.is_dir() and item.name in excluded_dirs:
                continue
            
            if item.is_file():
                item_type = "file"
            elif item.is_dir():
                item_type = "directory"    
            else:
                item_type = "other"
            
             # Create a relative path from the project root
            relative_path = item.relative_to(paths_object)
            
            
            item_details = {
                "name":item.name,
                "path":relative_path.as_posix(),
                "type":item_type
            }    
            list_items.append(item_details)
            
            # Explore nested directories
            if item.is_dir():
                insepect_directiory(item)
            
    insepect_directiory(paths_object)
    return{
        
            "valid":True, 
            "error":None,
            "items":list_items
        } 
        




def search_project(problem:str   , project_path :str) ->dir:
    
    project_result = list_project_items(project_path)

    
    if not project_result["valid"]:
        return project_result
    
    # Extract words from the problem dynamically
    
    search_terms = re.findall(
    r"/[A-Za-z_][A-Za-z0-9_/-]*|[A-Za-z_]+|\d+",
    problem
)
    
    project_root = Path(project_path)
    matches  = []
    
    for item in project_result.get("items", []):
    
        
        if item["type"]!= "file":
            continue
        
        file_path = project_root / item["path"]
        
        if file_path.suffix != ".py":
            continue
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number , line in enumerate(file , start=1):
                    
                    if any(term.lower()  in line.lower()
                           for term in search_terms):
                            
                            matches.append({
                                "path":item["path"],
                                "line_number":line_number,
                                "text":line.strip()
        
                            })
        except (OSError, UnicodeError):
            continue 
        
    return {
            "valid":True,
            "error":None,
            "project_path":project_path,
            "problem":problem,
            "search_terms":search_terms,
            "matches":matches,
             "total_matches": len(matches)
        }           
                 
        
    
    
    


result = search_project(
    problem="My /orders API is returning 500",
    project_path=r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\sample_project\app"
)

print(result)

