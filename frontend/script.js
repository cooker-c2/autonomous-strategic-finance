document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('queryInput');
    const generateBtn = document.getElementById('generateBtn');
    const forecastContainer = document.getElementById('forecastContainer');

    generateBtn.addEventListener('click', async () => {
        const query = queryInput.value;
        if (!query) {
            forecastContainer.innerHTML = '<div class="placeholder-text"><p>Please enter a query.</p></div>';
            return;
        }

        forecastContainer.innerHTML = `
            <div class="placeholder-text">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Generating forecast...</p>
            </div>
        `;
        generateBtn.disabled = true;

        try {
            // Updated to send a POST request to the correct endpoint
            const response = await fetch(`http://127.0.0.1:8000/forecast_excel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    business_unit: "saas_company", // Hardcoded for now
                    months: 12 // Hardcoded for now
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}. Message: ${errorText}`);
            }

            // The backend returns a file, so we handle the file download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'forecast.xlsx';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);

            forecastContainer.innerHTML = `
                <div class="placeholder-text">
                    <i class="fas fa-check-circle"></i>
                    <p>Forecast generated and downloaded!</p>
                </div>
            `;

        } catch (error) {
            console.error('Error fetching data:', error);
            forecastContainer.innerHTML = `
                <div class="placeholder-text">
                    <i class="fas fa-times-circle"></i>
                    <p>Failed to generate forecast. Error: ${error.message}</p>
                </div>
            `;
        } finally {
            generateBtn.disabled = false;
        }
    });
});