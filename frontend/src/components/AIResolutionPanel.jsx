function AIResolutionPanel({ isOpen, shipment, triageResult, loading }) {
  if (!isOpen) return null;

  const actions = triageResult?.recommended_actions;
  const hasRecommendedActions = Array.isArray(actions) && actions.length > 0;

  return (
    <div className="ai-panel">
      <h2 className="ai-panel-title">AI Resolution</h2>

      <div className="ai-panel-content">
        {loading ? (
          <p>Generating AI resolution...</p>
        ) : !shipment ? (
          <p>Select a risky shipment to view AI recommendations.</p>
        ) : (
          <>
            <p>
              <strong>Shipment ID:</strong> {shipment.shipment_id}
            </p>
            <p>
              <strong>Origin:</strong> {shipment.origin}
            </p>
            <p>
              <strong>Destination:</strong> {shipment.destination}
            </p>
            <p>
              <strong>Cargo Type:</strong> {shipment.cargo_type}
            </p>

            <hr />

            {hasRecommendedActions ? (
              actions.map((option) => (
                <div
                  key={option.option_id || option.strategy}
                  style={{ marginBottom: "16px" }}
                >
                  <p>
                    <strong>Strategy:</strong> {option.strategy ?? "N/A"}
                  </p>
                  <p>
                    <strong>New ETA:</strong> {option.new_eta ?? "N/A"}
                  </p>
                  <p>
                    <strong>Additional Cost:</strong>{" "}
                    {option.additional_cost_usd != null
                      ? `$${option.additional_cost_usd}`
                      : "N/A"}
                  </p>
                  <p>
                    <strong>AI Confidence:</strong>{" "}
                    {option.ai_confidence_score ?? "N/A"}
                  </p>
                  <p>
                    <strong>Reasoning:</strong> {option.reasoning ?? "N/A"}
                  </p>
                  <hr />
                </div>
              ))
            ) : triageResult?.summary ? (
              <>
                <p>
                  <strong>Summary:</strong> {triageResult.summary}
                </p>
                <p>
                  <strong>Recommended Action:</strong>{" "}
                  {triageResult.recommended_action ?? "N/A"}
                </p>
                <p>
                  <strong>Alternative Route:</strong>{" "}
                  {triageResult.alternative_route ?? "N/A"}
                </p>
                <p>
                  <strong>Estimated Delay:</strong>{" "}
                  {triageResult.estimated_delay ?? "N/A"}
                </p>
                <p>
                  <strong>Priority:</strong> {triageResult.priority ?? "N/A"}
                </p>
              </>
            ) : triageResult ? (
              <pre style={{ whiteSpace: "pre-wrap" }}>
                {JSON.stringify(triageResult, null, 2)}
              </pre>
            ) : (
              <p>No AI resolution available yet.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default AIResolutionPanel;
