/**
 * MoMo Data Analysis Dashboard - Chart Handler
 * Handles fetching data and rendering charts/tables for the dashboard
 */

class ChartHandler {
    constructor() {
        this.dashboardData = null;
        this.transactionData = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.filters = {
            dateFrom: null,
            dateTo: null,
            type: 'all',
            category: 'all',
            search: ''
        };
        
        // Chart instances
        this.charts = {
            transactionsByType: null,
            transactionsByCategory: null,
            transactionTrends: null,
            amountDistribution: null
        };
        
        // Initialize event listeners
        this.initEventListeners();
    }
    
    /**
     * Initialize event listeners for filters and pagination
     */
    initEventListeners() {
        // Filter form
        document.getElementById('filter-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateFilters();
            this.renderTransactionTable();
        });
        
        // Reset filters
        document.getElementById('reset-filters').addEventListener('click', () => {
            document.getElementById('filter-form').reset();
            this.resetFilters();
            this.renderTransactionTable();
        });
        
        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.renderTransactionTable();
            }
        });
        
        document.getElementById('next-page').addEventListener('click', () => {
            const totalPages = Math.ceil(this.getFilteredTransactions().length / this.itemsPerPage);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.renderTransactionTable();
            }
        });
    }
    
    /**
     * Fetch dashboard data from the server
     */
    async fetchData() {
        try {
            const response = await fetch('data/processed/dashboard.json');
            if (!response.ok) {
                throw new Error('Failed to fetch dashboard data');
            }
            
            this.dashboardData = await response.json();
            this.transactionData = this.dashboardData.transactions || [];
            
            // Initialize date filters with data range
            if (this.transactionData.length > 0) {
                const dates = this.transactionData.map(t => new Date(t.date));
                const minDate = new Date(Math.min(...dates));
                const maxDate = new Date(Math.max(...dates));
                
                document.getElementById('date-from').valueAsDate = minDate;
                document.getElementById('date-to').valueAsDate = maxDate;
            }
            
            return this.dashboardData;
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            this.showError('Failed to load dashboard data. Please try again later.');
            return null;
        }
    }
    
    /**
     * Update filters from form inputs
     */
    updateFilters() {
        const dateFrom = document.getElementById('date-from').value;
        const dateTo = document.getElementById('date-to').value;
        const type = document.getElementById('type-filter').value;
        const category = document.getElementById('category-filter').value;
        const search = document.getElementById('search-filter').value;
        
        this.filters = {
            dateFrom: dateFrom ? new Date(dateFrom) : null,
            dateTo: dateTo ? new Date(dateTo) : null,
            type: type || 'all',
            category: category || 'all',
            search: search.toLowerCase()
        };
        
        // Reset to first page when filters change
        this.currentPage = 1;
    }
    
    /**
     * Reset all filters to default values
     */
    resetFilters() {
        this.filters = {
            dateFrom: null,
            dateTo: null,
            type: 'all',
            category: 'all',
            search: ''
        };
        this.currentPage = 1;
    }
    
    /**
     * Get transactions filtered by current filter settings
     */
    getFilteredTransactions() {
        if (!this.transactionData) return [];
        
        return this.transactionData.filter(transaction => {
            const transactionDate = new Date(transaction.date);
            
            // Date filter
            if (this.filters.dateFrom && transactionDate < this.filters.dateFrom) return false;
            if (this.filters.dateTo && transactionDate > this.filters.dateTo) return false;
            
            // Type filter
            if (this.filters.type !== 'all' && transaction.type !== this.filters.type) return false;
            
            // Category filter
            if (this.filters.category !== 'all' && transaction.category !== this.filters.category) return false;
            
            // Search filter
            if (this.filters.search) {
                const searchFields = [
                    transaction.description,
                    transaction.phone,
                    transaction.reference,
                    transaction.type,
                    transaction.category
                ].map(field => field ? field.toLowerCase() : '');
                
                return searchFields.some(field => field.includes(this.filters.search));
            }
            
            return true;
        });
    }
    
    /**
     * Render the transaction table with current filters and pagination
     */
    renderTransactionTable() {
        const filteredData = this.getFilteredTransactions();
        const tableBody = document.getElementById('transaction-table-body');
        const pageInfo = document.getElementById('page-info');
        const totalItems = filteredData.length;
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        
        // Update page info
        pageInfo.textContent = `Page ${this.currentPage} of ${totalPages || 1} (${totalItems} transactions)`;
        
        // Clear table
        tableBody.innerHTML = '';
        
        // Calculate slice indices for current page
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = filteredData.slice(startIndex, endIndex);
        
        // Render table rows
        if (pageData.length === 0) {
            const emptyRow = document.createElement('tr');
            emptyRow.innerHTML = `<td colspan="7" class="empty-table">No transactions found</td>`;
            tableBody.appendChild(emptyRow);
        } else {
            pageData.forEach(transaction => {
                const row = document.createElement('tr');
                
                // Format date
                const date = new Date(transaction.date);
                const formattedDate = date.toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric'
                });
                
                // Format amount
                const amount = new Intl.NumberFormat('en-RW', {
                    style: 'currency',
                    currency: 'RWF'
                }).format(transaction.amount);
                
                row.innerHTML = `
                    <td>${formattedDate}</td>
                    <td>${transaction.description}</td>
                    <td>${transaction.phone || '-'}</td>
                    <td>${transaction.reference || '-'}</td>
                    <td>
                        <span class="badge ${transaction.type.toLowerCase()}">
                            ${transaction.type}
                        </span>
                    </td>
                    <td>${transaction.category}</td>
                    <td>${amount}</td>
                `;
                
                tableBody.appendChild(row);
            });
        }
        
        // Update pagination buttons state
        document.getElementById('prev-page').disabled = this.currentPage <= 1;
        document.getElementById('next-page').disabled = this.currentPage >= totalPages;
    }
    
    /**
     * Initialize and render all charts
     */
    renderCharts() {
        this.renderTransactionsByTypeChart();
        this.renderTransactionsByCategoryChart();
        this.renderTransactionTrendsChart();
        this.renderAmountDistributionChart();
    }
    
    /**
     * Render transactions by type pie chart
     */
    renderTransactionsByTypeChart() {
        const ctx = document.getElementById('transactions-by-type-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.transactionsByType) {
            this.charts.transactionsByType.destroy();
        }
        
        // Group transactions by type and count
        const typeData = {};
        this.transactionData.forEach(transaction => {
            if (!typeData[transaction.type]) {
                typeData[transaction.type] = 0;
            }
            typeData[transaction.type]++;
        });
        
        // Prepare chart data
        const labels = Object.keys(typeData);
        const data = Object.values(typeData);
        const backgroundColors = [
            '#3b82f6', // Blue
            '#ef4444', // Red
            '#10b981', // Green
            '#f59e0b', // Amber
            '#8b5cf6', // Purple
            '#ec4899'  // Pink
        ];
        
        // Create chart
        this.charts.transactionsByType = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: backgroundColors.slice(0, labels.length),
                    borderWidth: 1,
                    borderColor: '#0f172a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#f8fafc',
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Render transactions by category bar chart
     */
    renderTransactionsByCategoryChart() {
        const ctx = document.getElementById('transactions-by-category-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.transactionsByCategory) {
            this.charts.transactionsByCategory.destroy();
        }
        
        // Group transactions by category and sum amounts
        const categoryData = {};
        this.transactionData.forEach(transaction => {
            if (!categoryData[transaction.category]) {
                categoryData[transaction.category] = 0;
            }
            categoryData[transaction.category] += transaction.amount;
        });
        
        // Sort categories by amount
        const sortedCategories = Object.entries(categoryData)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8); // Limit to top 8 categories
        
        // Prepare chart data
        const labels = sortedCategories.map(item => item[0]);
        const data = sortedCategories.map(item => item[1]);
        
        // Create chart
        this.charts.transactionsByCategory = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Amount (RWF)',
                    data: data,
                    backgroundColor: '#fbbf24',
                    borderColor: '#f59e0b',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#f8fafc',
                            callback: function(value) {
                                return new Intl.NumberFormat('en-RW', {
                                    style: 'currency',
                                    currency: 'RWF',
                                    maximumFractionDigits: 0
                                }).format(value);
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#f8fafc',
                            maxRotation: 45,
                            minRotation: 45
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return new Intl.NumberFormat('en-RW', {
                                    style: 'currency',
                                    currency: 'RWF'
                                }).format(context.raw);
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Render transaction trends line chart
     */
    renderTransactionTrendsChart() {
        const ctx = document.getElementById('transaction-trends-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.transactionTrends) {
            this.charts.transactionTrends.destroy();
        }
        
        // Group transactions by month
        const monthlyData = {};
        this.transactionData.forEach(transaction => {
            const date = new Date(transaction.date);
            const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
            
            if (!monthlyData[monthYear]) {
                monthlyData[monthYear] = {
                    count: 0,
                    amount: 0
                };
            }
            
            monthlyData[monthYear].count++;
            monthlyData[monthYear].amount += transaction.amount;
        });
        
        // Sort months chronologically
        const sortedMonths = Object.keys(monthlyData).sort();
        
        // Format month labels
        const labels = sortedMonths.map(monthYear => {
            const [year, month] = monthYear.split('-');
            return new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        });
        
        // Prepare datasets
        const countData = sortedMonths.map(month => monthlyData[month].count);
        const amountData = sortedMonths.map(month => monthlyData[month].amount);
        
        // Create chart
        this.charts.transactionTrends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Transaction Count',
                        data: countData,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.2)',
                        borderWidth: 2,
                        tension: 0.3,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Transaction Amount',
                        data: amountData,
                        borderColor: '#fbbf24',
                        backgroundColor: 'rgba(251, 191, 36, 0.2)',
                        borderWidth: 2,
                        tension: 0.3,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: {
                            color: '#f8fafc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Count',
                            color: '#3b82f6'
                        },
                        ticks: {
                            color: '#f8fafc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Amount (RWF)',
                            color: '#fbbf24'
                        },
                        ticks: {
                            color: '#f8fafc',
                            callback: function(value) {
                                return new Intl.NumberFormat('en-RW', {
                                    style: 'currency',
                                    currency: 'RWF',
                                    notation: 'compact',
                                    compactDisplay: 'short'
                                }).format(value);
                            }
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.datasetIndex === 1) {
                                    label += new Intl.NumberFormat('en-RW', {
                                        style: 'currency',
                                        currency: 'RWF'
                                    }).format(context.raw);
                                } else {
                                    label += context.raw;
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Render amount distribution histogram
     */
    renderAmountDistributionChart() {
        const ctx = document.getElementById('amount-distribution-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts.amountDistribution) {
            this.charts.amountDistribution.destroy();
        }
        
        // Extract amounts
        const amounts = this.transactionData.map(t => t.amount);
        
        // Create bins for histogram
        const max = Math.max(...amounts);
        const binSize = max / 10; // 10 bins
        const bins = Array(10).fill(0);
        
        // Count transactions in each bin
        amounts.forEach(amount => {
            const binIndex = Math.min(Math.floor(amount / binSize), 9);
            bins[binIndex]++;
        });
        
        // Create labels for bins
        const labels = bins.map((_, i) => {
            const start = i * binSize;
            const end = (i + 1) * binSize;
            return `${new Intl.NumberFormat('en-RW', {
                style: 'currency',
                currency: 'RWF',
                maximumFractionDigits: 0
            }).format(start)} - ${new Intl.NumberFormat('en-RW', {
                style: 'currency',
                currency: 'RWF',
                maximumFractionDigits: 0
            }).format(end)}`;
        });
        
        // Create chart
        this.charts.amountDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Transactions',
                    data: bins,
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#f8fafc'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#f8fafc',
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    /**
     * Update dashboard statistics
     */
    updateStatistics() {
        if (!this.dashboardData) return;
        
        // Calculate statistics
        const totalTransactions = this.transactionData.length;
        const totalAmount = this.transactionData.reduce((sum, t) => sum + t.amount, 0);
        const avgAmount = totalAmount / totalTransactions || 0;
        
        // Count transaction types
        const typeCount = {};
        this.transactionData.forEach(t => {
            if (!typeCount[t.type]) typeCount[t.type] = 0;
            typeCount[t.type]++;
        });
        
        // Update DOM elements
        document.getElementById('total-transactions').textContent = totalTransactions.toLocaleString();
        document.getElementById('total-amount').textContent = new Intl.NumberFormat('en-RW', {
            style: 'currency',
            currency: 'RWF'
        }).format(totalAmount);
        document.getElementById('avg-transaction').textContent = new Intl.NumberFormat('en-RW', {
            style: 'currency',
            currency: 'RWF'
        }).format(avgAmount);
        
        // Update type-specific stats if they exist
        if (typeCount['CASH_IN']) {
            document.getElementById('cash-in-count').textContent = typeCount['CASH_IN'].toLocaleString();
        }
        if (typeCount['CASH_OUT']) {
            document.getElementById('cash-out-count').textContent = typeCount['CASH_OUT'].toLocaleString();
        }
    }
    
    /**
     * Show error message to user
     */
    showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        
        document.body.appendChild(errorElement);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorElement.classList.add('fade-out');
            setTimeout(() => {
                document.body.removeChild(errorElement);
            }, 500);
        }, 5000);
    }
    
    /**
     * Initialize the dashboard
     */
    async init() {
        // Show loading state
        document.getElementById('loading').style.display = 'flex';
        
        try {
            // Fetch data
            await this.fetchData();
            
            // Render UI components
            this.renderTransactionTable();
            this.renderCharts();
            this.updateStatistics();
            
            // Hide loading state
            document.getElementById('loading').style.display = 'none';
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showError('Failed to initialize dashboard. Please try again later.');
            document.getElementById('loading').style.display = 'none';
        }
    }
}

// Export ChartHandler class for use by app.js
// The initialization is handled by app.js to avoid conflicts
