from pathlib import Path


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
    if paths_object.is_file():
        print("this is file")
    elif paths_object.is_dir():
         print("this is directory")  
    
    list_items = []
    
    for item in paths_object.iterdir():
        list_items.append(item.name)
        
  
    
    return{
     
        "valid":True, 
        "error":None,
        "items":list_items
    } 
    

    
    
  
        
  
        
        
    
        

from pathlib import Path


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
            print("item" , item)
            
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
        

    
    
  
        
  
        
        
    
        

result = list_project_items(
    r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\sample_project"
)

print("result:", result)