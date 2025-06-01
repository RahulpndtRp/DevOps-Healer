"""Input intent classifier agent for SupportOps"""

from typing import Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from ..base import BaseAgent


class InputIntentResult(BaseModel):
    is_valid: bool = Field(
        description="Whether the input describes a real infrastructure incident"
    )
    reasoning: str = Field(description="Short reasoning for the classification")


class InputIntentClassifier(BaseAgent):
    """
    LLM-driven classifier agent for DevOps incident intake.
    Inherits from BaseAgent to reuse LLM and logging.
    Can run in autonomous (LLM) or deterministic (keyword) mode.
    """

    def __init__(self, autonomous_mode: bool = True):
        super().__init__(agent_id="input-intent-classifier", agent_type=None)
        self.autonomous_mode = autonomous_mode

        if self.autonomous_mode:
            self.classifier_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are an expert DevOps classifier.
Only answer 'yes' if the input clearly describes an infrastructure incident (e.g. CPU, memory, disk, storage, network, database, cloud resources, production issues, system errors, etc).
Otherwise, answer 'no'. Do NOT explain your answer.""",
                    ),
                    (
                        "human",
                        "Does the following describe an infrastructure-related incident?\n\n{description}",
                    ),
                ]
            )
            self.output_parser = StrOutputParser()

    async def classify(self, description: str) -> InputIntentResult:
        """
        Classify a description as a real incident or not, using LLM or fallback.
        """
        if self.autonomous_mode:
            try:
                chain = self.classifier_prompt | self.llm | self.output_parser
                response = await chain.ainvoke({"description": description})
                is_valid = response.strip().lower() in ["yes", "true"]
                return InputIntentResult(
                    is_valid=is_valid,
                    reasoning=(
                        "LLM classified as valid incident."
                        if is_valid
                        else "LLM classified as non-incident."
                    ),
                )
            except Exception as e:
                return InputIntentResult(
                    is_valid=False, reasoning=f"⚠️ LLM intent classification failed: {e}"
                )
        else:
            keywords = [
                "disk",
                "cpu",
                "memory",
                "database",
                "storage",
                "connectivity",
                "latency",
                "timeout",
                "performance",
                "kubernetes",
                "pod",
                "network",
                "failure",
                "incident",
                "outage",
                "production",
                "server",
                "resource",
                "degradation",
                "error",
                "cloud",
            ]
            prompt = description.lower()
            is_valid = any(kw in prompt for kw in keywords)
            return InputIntentResult(
                is_valid=is_valid,
                reasoning=(
                    "Keyword match found."
                    if is_valid
                    else "No keyword match; likely not an incident."
                ),
            )

    async def classify_input(self, state: Any) -> Any:
        """
        Node entrypoint for the workflow: classifies the input and chooses next agent.
        """
        incident = state.get("incident")
        description = getattr(incident, "description", "") if incident else ""
        result = await self.classify(description)
        # Attach to state for downstream steps
        state["is_intent_valid"] = result.is_valid
        state["intent_classification_reason"] = result.reasoning
        # Choose next agent based on intent
        state["current_agent"] = (
            "tribe_orchestrator" if result.is_valid else "fallback-handler"
        )
        state["workflow_status"] = "initialized"
        # Optional: log for debug
        print(
            f"🤖 [Classifier] Description: {description}\n   LLM result: {result.is_valid} / {result.reasoning}"
        )
        return state

    def fallback_handler(self, state: Any) -> Any:
        """
        Node entrypoint for the workflow: handles non-actionable inputs.
        """
        print(
            "❌ Not a valid DevOps incident. This appears to be a non-actionable input."
        )
        state["workflow_status"] = "non_actionable"
        state["current_agent"] = "none"
        return state

    async def execute(self, state: Any) -> Any:
        """Satisfy abstract base class, routes to classify_input for graph compatibility."""
        return await self.classify_input(state)
