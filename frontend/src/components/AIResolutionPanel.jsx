function AIResolutionPanel({ isOpen }) {
  if (!isOpen) return null;

  return (
    <div className="ai-panel">
      <h2 className="ai-panel-title">AI Resolution</h2>

      <div className="ai-panel-content">
        <p>No AI resolution available yet.</p>
        <p>
          Later, this panel will show rerouting suggestions and risk actions.
        </p>
      </div>
    </div>
  );
}

export default AIResolutionPanel;
