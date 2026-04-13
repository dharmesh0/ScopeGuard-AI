from app.services.agents.base import AgentContext, AgentResult
from app.services.container.manager import ContainerManager
from app.services.plugins.registry import builtin_plugins


class ReconAgent:
    def __init__(self) -> None:
        self.container_manager = ContainerManager()

    def run(self, context: AgentContext) -> AgentResult:
        logs = ["Recon agent starting safe plugin execution."]
        all_findings: list[dict] = []
        for plugin_name in builtin_plugins():
            logs.append(f"Running plugin: {plugin_name}")
            try:
                result = self.container_manager.execute_plugin(plugin_name, context.target)
                all_findings.extend(result.findings)
                logs.append(f"Plugin {plugin_name} completed with {len(result.findings)} findings.")
            except Exception as exc:  # noqa: BLE001
                logs.append(f"Plugin {plugin_name} failed safely: {exc}")
        return AgentResult(logs=logs, findings=all_findings)
