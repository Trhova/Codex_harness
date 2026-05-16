export function drawAlertPanel(host, telemetry) {
  const criticalRoutes = telemetry.routes.filter(routeStatus);
  host.innerHTML = `
    <section class="metric-row">
      <div><span class="label">Network load</span><strong>${telemetry.networkLoad}%</strong></div>
      <div><span class="label">Incidents</span><strong>${telemetry.incidents}</strong></div>
      <div><span class="label">Critical routes</span><strong>${criticalRoutes.length}</strong></div>
    </section>
  `;
}

export function drawRouteTable(host, routes) {
  host.innerHTML = `
    <h2>Corridors</h2>
    <table>
      <thead><tr><th>Route</th><th>Load</th><th>Headway</th><th>Status</th></tr></thead>
      <tbody>
        ${routes
          .map((route) => {
            const status = routeStatus(route) ? "critical" : "normal";
            return `<tr class="${status}"><td>${route.name}</td><td>${route.load}%</td><td>${route.headway} min</td><td>${status}</td></tr>`;
          })
          .join("")}
      </tbody>
    </table>
  `;
}

export function routeStatus(route) {
  return route.load > route.criticalLoadThreshold || route.delayMinutes >= 7;
}
