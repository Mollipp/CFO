"""Client for asking natural-language questions against a Databricks Genie Space.

Uses ``WorkspaceClient().genie`` (databricks-sdk's ``GenieAPI``) to start/continue a
conversation, waits for the AI response, and pulls out the answer text, generated SQL,
and query result rows.
"""

import pandas as pd

from src.config import USE_MOCKS, GENIE_SPACE_ID

GENIE_ROW_CAP = 100

_MOCK_ANSWER_TEXT = (
    "[MOCK Genie response] Q3 net interest income was EUR 412M, up 3.1% QoQ, "
    "driven by higher loan volumes in the corporate book. No live Genie Space "
    "is configured -- set GENIE_SPACE_ID (and Databricks auth) to enable live queries."
)

_MOCK_SQL = (
    "SELECT quarter, net_interest_income_eur_m\n"
    "FROM finance.gold.income_statement\n"
    "WHERE quarter = '2025-Q3'"
)

_MOCK_DATA = pd.DataFrame(
    [
        {"quarter": "2025-Q2", "net_interest_income_eur_m": 400},
        {"quarter": "2025-Q3", "net_interest_income_eur_m": 412},
    ]
)


def _mock_response() -> dict:
    return {
        "answer_text": _MOCK_ANSWER_TEXT,
        "sql": _MOCK_SQL,
        "data": _MOCK_DATA,
        "conversation_id": "mock-conversation-id",
    }


def _get_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()


def _extract_answer_text(message) -> str:
    parts = []
    for attachment in message.attachments or []:
        if attachment.text and attachment.text.content:
            parts.append(attachment.text.content)
    if parts:
        return "\n\n".join(parts)
    return message.content or ""


def _extract_query_attachment(message):
    for attachment in message.attachments or []:
        if attachment.query is not None:
            return attachment
    return None


def _rows_to_dataframe(query_result) -> pd.DataFrame:
    statement_response = query_result.statement_response
    if statement_response is None or statement_response.result is None:
        return pd.DataFrame()

    manifest = statement_response.manifest
    columns = (
        [col.name for col in manifest.schema.columns]
        if manifest and manifest.schema and manifest.schema.columns
        else None
    )

    data_array = statement_response.result.data_array or []
    capped_rows = data_array[:GENIE_ROW_CAP]

    if columns:
        return pd.DataFrame(capped_rows, columns=columns)
    return pd.DataFrame(capped_rows)


def ask_genie(question: str, conversation_id: str | None = None) -> dict:
    """Ask Genie a natural-language question and return its answer, SQL, and data.

    Starts a new Genie conversation, or continues an existing one when
    ``conversation_id`` is given. Waits (polls) until the response is complete,
    then extracts the text answer, the generated SQL (if any), and up to
    ``GENIE_ROW_CAP`` rows of query result data.
    """
    if USE_MOCKS:
        return _mock_response()

    if not GENIE_SPACE_ID:
        raise RuntimeError("GENIE_SPACE_ID is missing. Add it to the .env file.")

    client = _get_client()

    try:
        if conversation_id:
            message = client.genie.create_message_and_wait(
                space_id=GENIE_SPACE_ID,
                conversation_id=conversation_id,
                content=question,
            )
        else:
            message = client.genie.start_conversation_and_wait(
                space_id=GENIE_SPACE_ID,
                content=question,
            )

        if message.status and message.status.value == "FAILED":
            error_text = message.error.error if message.error else "Unknown error"
            raise RuntimeError(f"Genie query failed: {error_text}")

        answer_text = _extract_answer_text(message)

        sql = None
        data = pd.DataFrame()
        query_attachment = _extract_query_attachment(message)
        if query_attachment is not None:
            sql = query_attachment.query.query
            query_result = client.genie.get_message_attachment_query_result(
                space_id=GENIE_SPACE_ID,
                conversation_id=message.conversation_id,
                message_id=message.message_id,
                attachment_id=query_attachment.attachment_id,
            )
            data = _rows_to_dataframe(query_result)

        return {
            "answer_text": answer_text,
            "sql": sql,
            "data": data,
            "conversation_id": message.conversation_id,
        }
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Genie partner error: {exc}") from exc


if __name__ == "__main__":
    result = ask_genie("What was net interest income in the most recent quarter?")
    print("Answer:", result["answer_text"])
    print("SQL:", result["sql"])
    print("Conversation ID:", result["conversation_id"])
    print("Data:")
    print(result["data"])
