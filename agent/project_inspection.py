import ast
import re
from pathlib import Path

from logs.logger_config import logger


def validate_project_path(project_path:str):

    logger.info("Starting project path validation")
    logger.debug("Input project path: %s", project_path)

    # Step 1: Convert the path into a Path object

    project_path_obj = Path(project_path)

    logger.debug("Converted path into Path object: %s", project_path_obj)

    # Step 2: Check whether the path exists
    if not project_path_obj.exists():

        logger.warning("Project path does not exist: %s", project_path)

        return {
                    "valid":False,
                    "error": "PROJECT_PATH_NOT_FOUND"
                }

            # Step 3: Check whether the path is a directory

    if not project_path_obj.is_dir():

        logger.warning("Provided path is not a directory: %s", project_path)

        return{
                    "valid":False,
                    "error": "NOT_A_DIRECTORY",
                }

            # Step 4: All checks passed

    logger.info("Project path validation successful")

    return{
                "valid":True,
                "error":None
            }   


def list_project_items(project_path: str):

    logger.info("Starting project inspection")
    logger.debug("Project path: %s", project_path)

    validation_result = validate_project_path(project_path)

    logger.debug("Path validation result: %s", validation_result)

    if not validation_result["valid"]:

        logger.warning("Project inspection stopped: invalid path")

        return validation_result

    paths_object  = Path(project_path)

    excluded_dirs = {".git", ".venv", "venv"}
    list_items = []

    logger.debug("Excluded directories: %s", excluded_dirs)

    #  Inspect directories recursively
    def insepect_directiory(current_directiory :Path):

        logger.debug("Inspecting directory: %s", current_directiory)

        for item in current_directiory.iterdir():

            logger.debug("Found project item: %s", item)
            # print("item" , item)

            #Skip excluded directories completely

            if item.is_dir() and item.name in excluded_dirs:

                logger.debug("Skipping excluded directory: %s", item)
                continue

            if item.is_file():
                item_type = "file"
            elif item.is_dir():
                item_type = "directory"    
            else:
                item_type = "other"

            logger.debug("Detected item type: %s | Item: %s", item_type, item.name)

             # Create a relative path from the project root
            relative_path = item.relative_to(paths_object)

            logger.debug("Relative path: %s", relative_path)

            item_details = {
                "name":item.name,
                "path":relative_path.as_posix(),
                "type":item_type
            }

            logger.debug("Item details: %s", item_details)

            list_items.append(item_details)

            # Explore nested directories
            if item.is_dir():

                logger.debug("Entering nested directory: %s", item)
                insepect_directiory(item)

    insepect_directiory(paths_object)

    logger.info("Project inspection completed")
    logger.info("Total project items discovered: %d", len(list_items))

    return{

            "valid":True, 
            "error":None,
            "items":list_items
        } 


def extract_function_calls(line: str) -> list[str]:

    logger.debug("Extracting function calls from line: %s", line)

    pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\("

    calls = re.findall(pattern, line)

    logger.debug("Extracted function calls: %s", calls)

    return calls


def find_function_definition(function_name: str, project_path: str) -> list[dict]:

    logger.info("Searching function definition: %s", function_name)
    logger.debug("Project path: %s", project_path)

    project_result = list_project_items(project_path)

    if not project_result["valid"]:

        logger.warning("Cannot search function definition: invalid project")
        return []

    project_root = Path(project_path)
    definitions = []

    pattern = re.compile(
        rf"^\s*def\s+{re.escape(function_name)}\s*\("
    )

    logger.debug("Function definition search pattern: %s", pattern.pattern)

    for item in project_result.get("items", []):

        if item["type"] != "file":
            continue

        file_path = project_root / item["path"]

        if file_path.suffix != ".py":
            continue

        logger.debug("Searching function in file: %s", file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):

                    if pattern.search(line):

                        logger.info(
                            "Function definition found: %s | File: %s | Line: %d",
                            function_name, item["path"], line_number
                        )

                        definitions.append({
                            "name": function_name,
                            "path": item["path"],
                            "line_number": line_number,
                            "text": line.strip()
                        })

        except (OSError, UnicodeError):

            logger.warning("Could not read file: %s", file_path)
            continue

    logger.info(
        "Function definition search completed: %s | Total definitions: %d",
        function_name, len(definitions)
    )

    return definitions


def extract_calls_from_file(file_path: str) -> list[str]:

    logger.info("Extracting function calls from file: %s", file_path)

    calls = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:

                calls.extend(extract_function_calls(line))

        logger.debug("Function calls extracted from file: %s", calls)

    except (OSError, UnicodeError):

        logger.warning("Failed to read file: %s", file_path)
        return []

    return calls


def extract_function_body(file_path: str, function_name: str):

    logger.info(
        "Extracting function body: %s | File: %s",
        function_name, file_path
    )

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source_code = file.read()

        logger.debug("Source code loaded from: %s", file_path)

        tree = ast.parse(source_code)

        logger.debug("AST parsing successful: %s", file_path)

        for node in ast.walk(tree):

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

                logger.debug("Found function node: %s", node.name)

                if node.name == function_name:

                    logger.info("Matching function found: %s", function_name)

                    function_lines = source_code.splitlines()

                    start = node.lineno - 1
                    end = node.end_lineno

                    logger.debug(
                        "Function body line range: %d to %d",
                        start + 1, end
                    )

                    function_body = function_lines[start:end]

                    logger.debug("Extracted function body: %s", function_body)

                    return function_body

    except (OSError, UnicodeError, SyntaxError):

        logger.exception(
            "Failed to extract function body: %s",
            function_name
        )
        return []

    logger.warning("Function definition not found: %s", function_name)

    return []


def search_project(problem: str, project_path: str) -> dict:

    logger.info("========== SEARCH PROJECT STARTED ==========")
    logger.info("Problem received: %s", problem)
    logger.info("Project path received: %s", project_path)

    project_result = list_project_items(project_path)

    logger.debug("Project inspection result received")

    if not project_result["valid"]:

        logger.error("Search stopped: project path is invalid")
        return project_result

    # Extract words from the problem dynamically
    stop_words = {"my", "api", "is", "returning"}

    logger.debug("Stop words: %s", stop_words)

    search_terms = re.findall(
    r"/[A-Za-z_][A-Za-z0-9_/-]*|[A-Za-z_]+|\d+",
    problem
)

    logger.debug("Initially extracted search terms: %s", search_terms)

    search_terms = [
    term for term in search_terms
    if term.lower() not in stop_words
]

    logger.info("Final search terms: %s", search_terms)

    project_root = Path(project_path)
    matches  = []

    logger.info("Starting code search")

    for item in project_result.get("items", []):

        if item["type"]!= "file":
            continue

        file_path = project_root / item["path"]

        if file_path.suffix != ".py":
            continue

        logger.debug("Searching file: %s", file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number , line in enumerate(file , start=1):

                    if any(term.lower()  in line.lower()
                           for term in search_terms):

                        logger.info(
                            "Matching line found | File: %s | Line: %d | Text: %s",
                            item["path"], line_number, line.strip()
                        )

                        matches.append({
                                "path":item["path"],
                                "line_number":line_number,
                                "text":line.strip()

                            })

        except (OSError, UnicodeError):

            logger.warning("Could not search file: %s", file_path)
            continue

    logger.info("Initial code search completed")
    logger.info("Total matching lines: %d", len(matches))

    related_functions = []

    logger.info("Starting related function discovery")

    for match in matches:

        logger.debug("Processing matched file: %s", match["path"])

        matched_file = project_root / match["path"]

        function_calls = extract_calls_from_file(str(matched_file))

        logger.debug("Function calls in matched file: %s", function_calls)

        for funtion_naame in function_calls:

                logger.debug("Checking function body: %s", funtion_naame)

                function_body = extract_function_body(
                    str(matched_file), funtion_naame)

                if function_body:

                    logger.debug(
                        "Function body found for: %s",
                        funtion_naame
                    )

                    for line in function_body:

                        calls = extract_function_calls(line)

                        logger.debug(
                            "Calls extracted from function body: %s",
                            calls
                        )

                        related_functions.extend(calls)

    logger.info("Initial related functions: %s", related_functions)

    visited_functions = set()
    related_function_details = []  # ADD THIS LINE

    logger.debug("Visited functions set initialized")
    logger.debug("Related function details list initialized")

    function_queue = list(related_functions)
    MAX_FUNCTIONS = 50

    logger.info("Function tracing started")
    logger.debug("Initial function queue: %s", function_queue)
    logger.debug("Maximum functions allowed: %d", MAX_FUNCTIONS)

    while function_queue:

        logger.debug("Current function queue: %s", function_queue)

        function_name = function_queue.pop(0)

        logger.info("Processing function: %s", function_name)

        logger.debug("Remaining queue size: %d", len(function_queue))

        if len(visited_functions) >= MAX_FUNCTIONS:

             logger.warning(
                 "Maximum function processing limit reached: %d",
                 MAX_FUNCTIONS
             )

             break

        # Skip functions that have already been processed
        if function_name in visited_functions:

            logger.debug("Function already visited, skipping: %s", function_name)
            continue

        # Mark as visited
        visited_functions.add(function_name)

        logger.debug("Function added to visited set: %s", function_name)

        print("Processing function:", function_name)

        definitions = find_function_definition(
            function_name, project_path
        )

        logger.debug("Definitions returned: %s", definitions)

        print("Found definitions:", definitions)

        if not definitions:
            logger.warning("No definition found for function: %s", function_name)

        for definition in definitions:

            logger.info(
                "Processing definition: %s | File: %s | Line: %s",
                definition["name"],
                definition["path"],
                definition["line_number"]
            )

            definition_file = project_root / definition["path"]

            function_body = extract_function_body(
                str(definition_file), function_name
            )

            logger.debug("Function body received: %s", function_body)

            print("Function body:", function_body)

            function_calls = []

            for line in function_body:

                logger.debug("Analyzing function body line: %s", line)

                if re.match(r"^\s*(?:async\s+)?def\s+", line):

                    logger.debug("Skipping function definition line")
                    continue

                new_calls = extract_function_calls(line)

                logger.debug("New function calls detected: %s", new_calls)

                for call in new_calls:

                    if call not in function_calls:

                        function_calls.append(call)

                        logger.debug(
                            "Added to function_calls: %s",
                            call
                        )

                    if call not in related_functions:

                        related_functions.append(call)

                        logger.debug(
                            "Added to related_functions: %s",
                            call
                        )

                    if call not in visited_functions and call not in function_queue:

                        function_queue.append(call)

                        logger.info(
                            "New function added to queue: %s",
                            call
                        )

            logger.info(
                "Function tracing completed for: %s",
                function_name
            )

            logger.debug("Function calls discovered: %s", function_calls)

            function_detail = {
                "name": definition["name"],
                "path": definition["path"],
                "line_number": definition["line_number"],
                "body": function_body,
                "function_calls": function_calls
            }

            logger.debug("Function detail created: %s", function_detail)

            if not any(

                item["name"] == function_detail["name"]
                and item["path"] == function_detail["path"]
                for item in related_function_details
):

                related_function_details.append(function_detail)

                logger.info(
                    "Function detail added: %s",
                    function_detail["name"]
                )

            else:

                logger.debug(
                    "Duplicate function detail skipped: %s",
                    function_detail["name"]
                )

    logger.info("Function tracing loop completed")

    logger.info("Total visited functions: %d", len(visited_functions))
    logger.info("Total related functions: %d", len(related_functions))
    logger.info(
        "Total function details: %d",
        len(related_function_details)
    )

    logger.info("========== SEARCH PROJECT COMPLETED ==========")

    return {
            "valid":True,
            "error":None,
            "project_path":project_path,
            "problem":problem,
            "search_terms":search_terms,
            "matches":matches,
            "total_matches": len(matches),
            "related_functions": related_functions,

            "related_function_details": related_function_details
        }     


result = search_project(
    problem="My /orders API is returning 500",
    project_path=r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\sample_project\app"
)

print(result)
# calls = extract_function_calls(
#     "return get_all_orders()"
# )
# print("Detected calls:", calls)

# definitions = find_function_definition(
#     calls[0],
#     r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\sample_project\app"
# )
# print("Found definitions:", definitions)


# calls = extract_calls_from_file(
#     r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\sample_project\app\services\services.py"
# )

# print(calls)


# file_path = r"C:\Users\gaura\OneDrive\Documents\ai-software-engineering-agent\sample_project\app\services\services.py"

# body = extract_function_body(file_path, "fetch_orders")

# print("Function body:")

# for line in body:
#     print(line)