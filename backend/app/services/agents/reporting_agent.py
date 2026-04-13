from app.services.agents.base import AgentContext, AgentResult


class ReportingAgent:
    def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            logs=["Reporting agent finalized output package."],
            findings=context.findings,
            summary=context.summary,
        )

