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
               
        
    
    
  
        
  
        
        
    
        

result = validate_project_path(r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\tests\test_project_inspection.py")
print("result :" , result)