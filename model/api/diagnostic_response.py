from typing import Any, Dict, Optional

from .basic_response import BasicResponse

class DiagnosticResponse(BasicResponse):
    status: Optional[bool]
    gaitType: Optional[str]
    graphs: Optional[Dict[str, Any]]

