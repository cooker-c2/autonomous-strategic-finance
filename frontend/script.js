document.addEventListener('DOMContentLoaded', () => {
// Get references to HTML elements
const queryInput = document.getElementById('query-input');
const generateBtn = document.getElementById('generate-btn');
const forecastContainer = document.getElementById('forecast-container');
const placeholderText = document.getElementById('placeholder-text');

generateBtn.addEventListener('click', async () => {
    const query = queryInput.value;
    if (!query) {
        forecastContainer.innerHTML = '<div class="text-center text-red-500"><p>Please enter a query.</p></div>';
        return;
    }

    // Show loading state
    forecastContainer.innerHTML = `
        <div class="flex flex-col items-center text-gray-400">
            <div class="spinner"></div>
            <p class="mt-4 text-lg">Generating forecast...</p>
        </div>
    `;
    generateBtn.disabled = true;

    try {
        // Make the API call to the backend
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

        // Handle the file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'forecast.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        // Show success message
        forecastContainer.innerHTML = `
            <div class="flex flex-col items-center text-green-400">
                <i class="fas fa-check-circle text-4xl mb-4"></i>
                <p class="text-lg">Forecast generated and downloaded!</p>
            </div>
        `;

    } catch (error) {
        console.error('Error fetching data:', error);
        forecastContainer.innerHTML = `
            <div class="flex flex-col items-center text-red-400">
                <i class="fas fa-times-circle text-4xl mb-4"></i>
                <p class="text-lg">Failed to generate forecast. Error: ${error.message}</p>
            </div>
        `;
    } finally {
        generateBtn.disabled = false;
    }
});

});