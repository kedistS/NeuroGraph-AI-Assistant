"""Pipeline API endpoints."""  
import os  
import tempfile  
from typing import List  
from fastapi import APIRouter, UploadFile, File, Form, HTTPException  
from ..services.orchestration_service import OrchestrationService  
from ..config.settings import settings  
  
router = APIRouter()  
orchestration_service = OrchestrationService()  
  
@router.post("/generate-graph")  
async def generate_graph(  
    files: List[UploadFile] = File(...),  
    config: str = Form(...),  
    schema_json: str = Form(...),  
    writer_type: str = Form("networkx")  
):  
    """Generate NetworkX graph from CSV files."""  
    # Validate all files are CSV  
    for file in files:  
        if not file.filename.endswith('.csv'):  
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")  
      
    # Save uploaded files to temporary directory  
    temp_dir = tempfile.mkdtemp()  
    csv_file_paths = []  
      
    try:  
        for file in files:  
            file_path = os.path.join(temp_dir, file.filename)  
            with open(file_path, "wb") as f:  
                content = await file.read()  
                f.write(content)  
            csv_file_paths.append(file_path)  
          
        result = await orchestration_service.generate_networkx(
            csv_files=csv_file_paths,
            config=config,
            schema_json=schema_json,
            writer_type=writer_type,
            tenant_id="default"
        )
          
        return result
          
    finally:  
        import shutil  
        if os.path.exists(temp_dir):  
            shutil.rmtree(temp_dir)

@router.post("/mine-patterns")
async def mine_patterns(
    job_id: str = Form(...),
    min_pattern_size: int = Form(5),
    max_pattern_size: int = Form(10),
    min_neighborhood_size: int = Form(5),
    max_neighborhood_size: int = Form(10),
    n_neighborhoods: int = Form(2000),
    n_trials: int = Form(100),
    radius: int = Form(3),
    graph_type: str = Form("directed"),
    search_strategy: str = Form("greedy"),
    sample_method: str = Form("tree")
):
    """ Mine patterns from NetworkX graph with custom configuration."""
    
    mining_config = {
        'min_pattern_size': min_pattern_size,
        'max_pattern_size': max_pattern_size,
        'min_neighborhood_size': min_neighborhood_size,
        'max_neighborhood_size': max_neighborhood_size,
        'n_neighborhoods': n_neighborhoods,
        'n_trials': n_trials,
        'radius': radius,
        'graph_type': graph_type,
        'search_strategy': search_strategy,
        'sample_method': sample_method
    }
    
    result = await orchestration_service.mine_patterns(
        job_id=job_id,
        mining_config=mining_config
    )
    
    return result