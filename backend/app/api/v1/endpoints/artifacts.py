from app.agents.coding_agent import CodingAgent
from app.core.deps import get_coding_agent
from app.schemas import CodeArtifact
from fastapi import APIRouter, Depends, HTTPException, Response

router = APIRouter()


@router.get("/{artifact_id}", response_model=CodeArtifact)
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


@router.get("/{artifact_id}/download")
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
