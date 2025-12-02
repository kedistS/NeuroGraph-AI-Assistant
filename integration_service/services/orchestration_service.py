"""Main orchestration service for pipeline coordination."""  
import os  
import uuid  
import httpx  
import tempfile  
import shutil
from typing import Dict, Any, List  
from .miner_service import MinerService  
from ..config.settings import settings  
  
class OrchestrationService:  
    """Main pipeline orchestrator."""  
            
    def __init__(self):  
        self.miner_service = MinerService()  
        self.atomspace_url = settings.atomspace_url  
        self.timeout = settings.atomspace_timeout  
        self.local_output_dir = "/app/output"
    
    async def generate_networkx(
        self,
        csv_files: List[str],
        config: str,
        schema_json: str,
        writer_type: str,
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        """Generate NetworkX graph from CSV files."""
        try:
            job_id = str(uuid.uuid4())
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:  
                config_file.write(config)  
                config_path = config_file.name  
                
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as schema_file:  
                schema_file.write(schema_json)  
                schema_path = schema_file.name  
                
            try:  
                async with httpx.AsyncClient(timeout=self.timeout) as client:  
                    files = []  
                    for csv_file_path in csv_files:  
                        csv_file = open(csv_file_path, 'rb')  
                        files.append(('files', (os.path.basename(csv_file_path), csv_file, 'text/csv')))  
                    
                    data = {  
                        'config': config,  
                        'schema_json': schema_json,  
                        'writer_type': writer_type,  
                        'tenant_id': tenant_id  
                    }  
                        
                    response = await client.post(  
                        f"{self.atomspace_url}/api/load",  
                        files=files,  
                        data=data  
                    )  
                        
                    for _, (_, file_obj, _) in files:  
                        file_obj.close()  
                        
                    if response.status_code != 200:  
                        raise RuntimeError(f"AtomSpace returned {response.status_code}: {response.text}")  
                        
                    result = response.json()  
                    
                networkx_file = f"/shared/output/{result['job_id']}/networkx_graph.pkl"  
                    
                return {
                    "job_id": result['job_id'],
                    "status": "success",
                    "networkx_file": networkx_file
                }
                    
            finally:  
                os.unlink(config_path)  
                os.unlink(schema_path)
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def mine_patterns(
        self,
        job_id: str,
        mining_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            # Verify NetworkX file exists
            networkx_file = f"/shared/output/{job_id}/networkx_graph.pkl"
            if not os.path.exists(networkx_file):
                raise FileNotFoundError(f"NetworkX file not found for job_id: {job_id}")
            
            # Mine motifs with config
            await self.miner_service.mine_motifs(
                networkx_file,
                job_id=job_id,
                mining_config=mining_config
            )
            
            local_paths = self._copy_to_local_output(job_id)
            
            return {
                "job_id": job_id,
                "status": "success",
                "output_paths": local_paths
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _copy_to_local_output(self, job_id: str) -> Dict[str, str]:
        """Copy results from shared volume to local directory and return paths."""
        shared_job_dir = f"/shared/output/{job_id}"
        local_job_dir = f"{self.local_output_dir}/{job_id}"
        
        os.makedirs(local_job_dir, exist_ok=True)
        
        shared_results = f"{shared_job_dir}/results"
        local_results = f"{local_job_dir}/results"
        if os.path.exists(shared_results):
            if os.path.exists(local_results):
                shutil.rmtree(local_results)
            shutil.copytree(shared_results, local_results)
        
        shared_plots = f"{shared_job_dir}/plots"
        local_plots = f"{local_job_dir}/plots"
        if os.path.exists(shared_plots):
            if os.path.exists(local_plots):
                shutil.rmtree(local_plots)
            shutil.copytree(shared_plots, local_plots)
        
        return {
            "results": f"./integration_service/output/{job_id}/results",
            "plots": f"./integration_service/output/{job_id}/plots"
        }