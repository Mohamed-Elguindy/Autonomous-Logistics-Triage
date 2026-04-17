function AIResolutionPanel({ isOpen, shipment, triageResult, loading, risk }) {
  if (!isOpen) return null;

  const actions = triageResult?.recommended_actions;
  const hasRecommendedActions = Array.isArray(actions) && actions.length > 0;

  return (
    <aside className="main-card ai-panel">
      <div className="card-header">
        <div>
          <h2>AI Resolution</h2>
          <p>Suggested mitigation strategies and route alternatives</p>
        </div>
      </div>

      <div className="ai-panel-content">
        {loading ? (
          <p className="info-text">Generating AI resolution...</p>
        ) : !shipment ? (
          <div className="empty-state">
            <h3>No shipment selected</h3>
            <p>Select a risky shipment marker to view AI recommendations.</p>
          </div>
        ) : (
          <>
            <div className="info-section">
              <h3>Shipment Overview</h3>
              <div className="info-grid">
                <div>
                  <span>ID: </span>
                  <strong>{shipment.shipment_id}</strong>
                </div>
                <div>
                  <span>Origin: </span>
                  <strong>{shipment.origin}</strong>
                </div>
                <div>
                  <span>Destination: </span>
                  <strong>{shipment.destination}</strong>
                </div>
                <div>
                  <span>Cargo: </span>
                  <strong>{shipment.cargo_type}</strong>
                </div>
              </div>
            </div>

            {risk && (
              <div className="info-section">
                <h3>Risk Summary</h3>
                <div className="info-grid">
                  <div>
                    <span>Status: </span>
                    <strong>{risk.risk_detected ? "Detected" : "Clear"}</strong>
                  </div>
                  <div>
                    <span>Type: </span>
                    <strong>{risk.risk_details?.type ?? "N/A"}</strong>
                  </div>
                  <div>
                    <span>Severity: </span>
                    <strong>{risk.risk_details?.severity ?? "N/A"}</strong>
                  </div>
                  <div>
                    <span>Source: </span>
                    <strong>{risk.risk_details?.source ?? "N/A"}</strong>
                  </div>
                </div>

                {risk.risk_details?.description && (
                  <p className="risk-description">
                    {risk.risk_details.description}
                  </p>
                )}
              </div>
            )}

            {hasRecommendedActions ? (
              <div className="actions-list">
                {actions.map((option) => (
                  <div
                    className="action-card"
                    key={option.option_id || option.strategy}
                  >
                    <div className="action-card-header">
                      <h3>{option.strategy ?? "Recommended Strategy"}</h3>
                      <span className="confidence-badge">
                        Confidence: {option.ai_confidence_score ?? "N/A"}
                      </span>
                    </div>

                    <div className="info-grid">
                      <div>
                        <span>New ETA: </span>
                        <strong>{option.new_eta ?? "N/A"}</strong>
                      </div>
                      <div>
                        <span>Added Cost: </span>
                        <strong>
                          {option.additional_cost_usd != null
                            ? `$${option.additional_cost_usd}`
                            : "N/A"}
                        </strong>
                      </div>
                    </div>

                    <p className="reasoning-text">
                      {option.reasoning ?? "No reasoning provided."}
                    </p>
                  </div>
                ))}
              </div>
            ) : triageResult?.message ? (
              <p className="info-text">{triageResult.message}</p>
            ) : (
              <div className="empty-state">
                <h3>No AI resolution available</h3>
                <p>No recommendation data has been returned yet.</p>
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );
}

export default AIResolutionPanel;
