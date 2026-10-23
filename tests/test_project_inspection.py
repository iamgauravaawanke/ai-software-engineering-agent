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
    
    list_items = []
    
    for item in paths_object.iterdir():
        list_items.append(item.name)
    
    return{
     
        "valid":True, 
        "error":None,
        "items":list_items
    } 
    

    
    
  
        
  
        
        
    
        

result = list_project_items(r"C:\Usess\gaura\OneDrive\Documents\ai-software-engineering-agent")
print("result :" , result)