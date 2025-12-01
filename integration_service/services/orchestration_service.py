"""Main orchestration service for pipeline coordination."""  
import os  
import uuid  
import httpx  
import tempfile  
from typing import Dict, Any, List  
from .miner_service import MinerService  
from ..config.settings import settings  
  
class OrchestrationService:  
    """Main pipeline orchestrator."""  
            
    def __init__(self):  
        self.miner_service = MinerService()  
        self.atomspace_url = settings.atomspace_url  
        self.timeout = settings.atomspace_timeout  
            
    async def execute_mining_pipeline(  
        self,  
        csv_files: List[str],  
        config: str,  
        schema_json: str,  
        writer_type: str,  
        tenant_id: str = "default"  
    ) -> Dict[str, Any]:  
        """Execute complete pipeline: CSV → NetworkX → Miner."""  
        try:  
            # Step 1: Generate NetworkX using AtomSpace Builder  
            networkx_result = await self._generate_networkx(  
                csv_files, config, schema_json, writer_type, tenant_id  
            )  
                
            # Step 2: Mine motifs using Neural Miner  
            motifs_result = await self._mine_motifs(networkx_result['networkx_file'])  
                
            return {  
                "job_id": networkx_result['job_id'],  
                "status": "success",  
                "motifs": motifs_result['motifs'],  
                "statistics": motifs_result['statistics']  
            }  
                
        except Exception as e:  
            return {"status": "error", "error": str(e)}  
        
    async def _generate_networkx(  
        self,  
        csv_files: List[str],  
        config: str,  
        schema_json: str,  
        writer_type: str,  
        tenant_id: str = "default"  
    ) -> Dict[str, Any]:  
        """Generate NetworkX using AtomSpace Builder."""  
        job_id = str(uuid.uuid4())  # Generate job_id internally  
          
        # Prepare files for AtomSpace Builder  
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:  
            config_file.write(config)  
            config_path = config_file.name  
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as schema_file:  
            schema_file.write(schema_json)  
            schema_path = schema_file.name  
            
        try:  
            # Call AtomSpace Builder with files  
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
                    
                # Close all file handles  
                for _, (_, file_obj, _) in files:  
                    file_obj.close()  
                    
                if response.status_code != 200:  
                    raise RuntimeError(f"AtomSpace returned {response.status_code}: {response.text}")  
                    
                result = response.json()  
                
            # NetworkX file path in shared volume  
            networkx_file = f"/shared/output/{result['job_id']}/networkx_graph.pkl"  
                
            return {  
                "job_id": result['job_id'],  
                "networkx_file": networkx_file  
            }  
                
        finally:  
            # Cleanup temporary files  
            os.unlink(config_path)  
            os.unlink(schema_path)  
        
    async def _mine_motifs(self, networkx_file_path: str) -> Dict[str, Any]:  
        """Mine motifs using Neural Miner service."""  
        return await self.miner_service.mine_motifs(networkx_file_path)