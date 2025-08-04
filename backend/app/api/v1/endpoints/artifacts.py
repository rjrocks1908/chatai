from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from app.schemas import ArtifactRequest, ArtifactResponse, CodeArtifact
from app.agents.coding_agent import CodingAgent
from app.core.deps import get_coding_agent
from app.utils.validators import InputValidator
from app.core.exceptions import InvalidRequestException

router = APIRouter()


@router.get("/artifacts/{artifact_id}", response_model=CodeArtifact)
async def get_artifact(
    artifact_id: str, agent: CodingAgent = Depends(get_coding_agent)
) -> CodeArtifact:
    """Get a specific artifact by ID"""
    try:
        artifact = agent.get_artifact(artifact_id)

        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")

        return artifact

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get artifact: {str(e)}")


# @router.get("/sessions/{session_id}/artifacts", response_model=ArtifactResponse)
# async def get_session_artifacts(
#     session_id: str, agent: CodingAgent = Depends(get_coding_agent)
# ) -> ArtifactResponse:
#     """Get all artifacts for a session"""
#     try:
#         # Validate session ID
#         if not InputValidator.validate_session_id(session_id):
#             raise HTTPException(status_code=400, detail="Invalid session ID")

#         artifacts = agent.get_session_artifacts(session_id)

#         return ArtifactResponse(artifacts=artifacts, total=len(artifacts))

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to get artifacts: {str(e)}"
#         )


# @router.get("/messages/{message_id}/artifacts", response_model=ArtifactResponse)
# async def get_message_artifacts(
#     message_id: str, agent: CodingAgent = Depends(get_coding_agent)
# ) -> ArtifactResponse:
#     """Get all artifacts for a specific message"""
#     try:
#         artifacts = agent.artifact_service.get_artifacts_by_message(message_id)

#         return ArtifactResponse(artifacts=artifacts, total=len(artifacts))

#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to get artifacts: {str(e)}"
#         )


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: str, agent: CodingAgent = Depends(get_coding_agent)
):
    """Download an artifact as a file"""
    try:
        artifact = agent.get_artifact(artifact_id)

        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")

        # Determine file extension based on language/type
        extension_map = {
            "python": "py",
            "javascript": "js",
            "html": "html",
            "css": "css",
            "jsx": "jsx",
            "typescript": "ts",
            "json": "json",
            "markdown": "md",
            "bash": "sh",
            "sql": "sql",
        }

        extension = extension_map.get(artifact.language.lower(), "txt")
        filename = f"{artifact.title.replace(' ', '_').lower()}.{extension}"

        # Determine content type
        content_type_map = {
            "py": "text/x-python",
            "js": "application/javascript",
            "html": "text/html",
            "css": "text/css",
            "jsx": "text/jsx",
            "ts": "application/typescript",
            "json": "application/json",
            "md": "text/markdown",
            "sh": "text/x-shellscript",
            "sql": "application/sql",
        }

        content_type = content_type_map.get(extension, "text/plain")

        return Response(
            content=artifact.content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": content_type,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download artifact: {str(e)}"
        )


# @router.delete("/artifacts/{artifact_id}")
# async def delete_artifact(
#     artifact_id: str, agent: CodingAgent = Depends(get_coding_agent)
# ):
#     """Delete an artifact"""
#     try:
#         success = agent.artifact_service.delete_artifact(artifact_id)

#         if not success:
#             raise HTTPException(status_code=404, detail="Artifact not found")

#         return {"message": "Artifact deleted successfully", "artifact_id": artifact_id}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to delete artifact: {str(e)}"
#         )


# @router.put("/artifacts/{artifact_id}")
# async def update_artifact(
#     artifact_id: str, updates: dict, agent: CodingAgent = Depends(get_coding_agent)
# ):
#     """Update an artifact"""
#     try:
#         # Validate allowed fields for update
#         allowed_fields = {"title", "description", "content", "metadata"}
#         update_data = {k: v for k, v in updates.items() if k in allowed_fields}

#         if not update_data:
#             raise HTTPException(status_code=400, detail="No valid fields to update")

#         # Validate content if being updated
#         if "content" in update_data:
#             artifact = agent.get_artifact(artifact_id)
#             if artifact:
#                 validation_result = InputValidator.validate_code_content(
#                     update_data["content"], artifact.language
#                 )
#                 if not validation_result["is_valid"]:
#                     raise HTTPException(
#                         status_code=400,
#                         detail=f"Invalid code content: {'; '.join(validation_result['issues'])}",
#                     )

#         updated_artifact = agent.artifact_service.update_artifact(
#             artifact_id, update_data
#         )

#         if not updated_artifact:
#             raise HTTPException(status_code=404, detail="Artifact not found")

#         return updated_artifact

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to update artifact: {str(e)}"
#         )


# @router.get("/artifacts/stats")
# async def get_artifact_stats(agent: CodingAgent = Depends(get_coding_agent)):
#     """Get global artifact statistics"""
#     try:
#         stats = agent.artifact_service.get_artifact_stats()
#         return stats

#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to get artifact stats: {str(e)}"
#         )


# @router.post("/artifacts/{artifact_id}/validate")
# async def validate_artifact(
#     artifact_id: str, agent: CodingAgent = Depends(get_coding_agent)
# ):
#     """Validate an artifact's code content"""
#     try:
#         artifact = agent.get_artifact(artifact_id)

#         if not artifact:
#             raise HTTPException(status_code=404, detail="Artifact not found")

#         validation_result = InputValidator.validate_code_content(
#             artifact.content, artifact.language
#         )

#         return {
#             "artifact_id": artifact_id,
#             "validation": validation_result,
#             "is_valid": validation_result["is_valid"],
#             "issues": validation_result.get("issues", []),
#             "warnings": validation_result.get("warnings", []),
#             "metrics": validation_result.get("metrics", {}),
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to validate artifact: {str(e)}"
#         )


# @router.get("/artifacts/{artifact_id}/preview")
# async def get_artifact_preview(
#     artifact_id: str, agent: CodingAgent = Depends(get_coding_agent)
# ):
#     """Get a preview-ready version of an artifact"""
#     try:
#         artifact = agent.get_artifact(artifact_id)

#         if not artifact:
#             raise HTTPException(status_code=404, detail="Artifact not found")

#         # For HTML artifacts, return content directly
#         if artifact.type.value == "html" or artifact.language == "html":
#             return Response(content=artifact.content, media_type="text/html")

#         # For other runnable types, wrap in basic HTML
#         if artifact.is_runnable:
#             if artifact.language in ["javascript", "js"]:
#                 preview_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <title>{artifact.title}</title>
#     <meta charset="utf-8">
# </head>
# <body>
#     <h1>{artifact.title}</h1>
#     <div id="output"></div>
#     <script>
# {artifact.content}
#     </script>
# </body>
# </html>"""
#                 return Response(content=preview_content, media_type="text/html")

#             elif artifact.language == "css":
#                 preview_content = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <title>{artifact.title}</title>
#     <meta charset="utf-8">
#     <style>
# {artifact.content}
#     </style>
# </head>
# <body>
#     <h1>{artifact.title}</h1>
#     <div class="demo-content">
#         <p>This is a demo paragraph to show the CSS styles.</p>
#         <button>Sample Button</button>
#         <div class="container">Sample container div</div>
#     </div>
# </body>
# </html>"""
#                 return Response(content=preview_content, media_type="text/html")

#         # For non-runnable artifacts, return formatted code
#         return {
#             "artifact_id": artifact_id,
#             "title": artifact.title,
#             "language": artifact.language,
#             "content": artifact.content,
#             "is_runnable": artifact.is_runnable,
#             "preview_available": False,
#             "message": "This artifact is not directly runnable in a browser preview.",
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to get artifact preview: {str(e)}"
#         )
