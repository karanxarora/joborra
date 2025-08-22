function jobDashboard() {
    return {
        // Data
        jobs: [],
        stats: {},
        loading: false,
        isLoggedIn: false,
        user: null,
        
        // Filters
        filters: {
            search: '',
            location: '',
            visa_sponsorship: '',
            experience_level: '',
            student_friendly: false,
            source: ''
        },
        
        // Pagination
        currentPage: 1,
        itemsPerPage: 12,
        
        // Sorting
        sortBy: 'scraped_at',
        sortOrder: 'desc',
        
        // Search debounce
        searchTimeout: null,
        
        // API base URL
        apiBase: 'http://localhost:8000',
        
        // Computed properties
        get filteredJobs() {
            // Since we're now using server-side filtering, just return all jobs
            // The filtering is done by the API when loadJobs() is called
            console.log('filteredJobs getter called, returning', this.jobs.length, 'jobs');
            return this.jobs;
        },
        
        get sortedJobs() {
            return [...this.filteredJobs].sort((a, b) => {
                let aValue = a[this.sortBy];
                let bValue = b[this.sortBy];
                
                // Handle nested properties
                if (this.sortBy === 'company_name') {
                    aValue = a.company.name;
                    bValue = b.company.name;
                }
                
                // Handle null/undefined values
                if (aValue == null) aValue = '';
                if (bValue == null) bValue = '';
                
                // Convert to comparable values
                if (typeof aValue === 'string') {
                    aValue = aValue.toLowerCase();
                    bValue = bValue.toLowerCase();
                }
                
                if (this.sortOrder === 'desc') {
                    return bValue > aValue ? 1 : bValue < aValue ? -1 : 0;
                } else {
                    return aValue > bValue ? 1 : aValue < bValue ? -1 : 0;
                }
            });
        },
        
        get totalPages() {
            return Math.ceil(this.filteredJobs.length / this.itemsPerPage);
        },
        
        get paginatedJobs() {
            const start = (this.currentPage - 1) * this.itemsPerPage;
            const end = start + this.itemsPerPage;
            return this.sortedJobs.slice(start, end);
        },
        
        get visiblePages() {
            const pages = [];
            const total = this.totalPages;
            const current = this.currentPage;
            
            // Always show first page
            if (total > 0) pages.push(1);
            
            // Show pages around current page
            for (let i = Math.max(2, current - 2); i <= Math.min(total - 1, current + 2); i++) {
                if (!pages.includes(i)) pages.push(i);
            }
            
            // Always show last page
            if (total > 1 && !pages.includes(total)) pages.push(total);
            
            return pages.sort((a, b) => a - b);
        },
        
        // Methods
        async init() {
            console.log('Dashboard initializing...');
            this.checkAuthStatus();
            await this.loadStats();
            await this.loadJobs();
        },
        
        checkAuthStatus() {
            const token = localStorage.getItem('token');
            const user = localStorage.getItem('user');
            
            if (token && user) {
                this.isLoggedIn = true;
                this.user = JSON.parse(user);
            } else {
                this.isLoggedIn = false;
                this.user = null;
            }
        },
        
        async logout() {
            console.log('Logout function called');
            try {
                const token = localStorage.getItem('token');
                console.log('Token found:', !!token);
                
                if (token) {
                    console.log('Calling logout API...');
                    // Call logout API
                    const response = await fetch(`${this.apiBase}/auth/session/logout`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });
                    console.log('Logout API response:', response.status);
                    
                    if (response.ok) {
                        const data = await response.json();
                        console.log('Logout API success:', data);
                    }
                }
            } catch (error) {
                console.error('Logout API error:', error);
            } finally {
                console.log('Clearing localStorage and redirecting...');
                // Clear local storage
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                
                // Update state
                this.isLoggedIn = false;
                this.user = null;
                
                // Redirect to home
                console.log('Redirecting to home page...');
                window.location.href = '/';
            }
        },
        
        // Debounced search
        onSearchInput() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.applyFilters();
            }, 500);
        },
        
        async loadStats() {
            try {
                console.log('Loading stats from:', `${this.apiBase}/jobs/stats`);
                const response = await fetch(`${this.apiBase}/jobs/stats`);
                if (response.ok) {
                    this.stats = await response.json();
                    console.log('Loaded stats:', this.stats);
                } else {
                    console.error('Failed to load stats:', response.status, response.statusText);
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },
        
        async loadJobs() {
            this.loading = true;
            try {
                // Build filter parameters
                const params = new URLSearchParams({
                    per_page: '100', // Maximum allowed by API
                    page: '1'
                });
                
                // Add active filters to API request
                if (this.filters.search && this.filters.search.trim()) {
                    params.append('search', this.filters.search.trim());
                }
                if (this.filters.location && this.filters.location.trim()) {
                    params.append('location', this.filters.location.trim());
                }
                if (this.filters.visa_sponsorship !== '') {
                    params.append('visa_sponsorship', this.filters.visa_sponsorship);
                }
                if (this.filters.experience_level && this.filters.experience_level.trim()) {
                    params.append('experience_level', this.filters.experience_level.trim());
                }
                if (this.filters.student_friendly) {
                    params.append('international_student_friendly', 'true');
                }
                if (this.filters.source && this.filters.source.trim()) {
                    params.append('source_website', this.filters.source.trim());
                }
                
                // Load jobs with server-side filtering
                let allJobs = [];
                let page = 1;
                let totalPages = 1;
                
                do {
                    params.set('page', page.toString());
                    
                    const url = `${this.apiBase}/jobs/search?${params}`;
                    console.log(`Loading jobs page ${page} from:`, url);
                    console.log('Request URL params:', params.toString());
                    const response = await fetch(url);
                    
                    if (response.ok) {
                        const data = await response.json();
                        allJobs = allJobs.concat(data.jobs || []);
                        totalPages = data.total_pages || 1;
                        page++;
                        
                        // Limit to first 10 pages (1000 jobs) to avoid overwhelming the browser
                        if (page > 10) break;
                    } else {
                        console.error('Failed to load jobs:', response.status, response.statusText);
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        break;
                    }
                } while (page <= totalPages);
                
                this.jobs = allJobs;
                console.log('Loaded total jobs:', this.jobs.length);
                
            } catch (error) {
                console.error('Error loading jobs:', error);
            } finally {
                this.loading = false;
            }
        },
        
        async refreshData() {
            await this.loadStats();
            await this.loadJobs();
        },
        
        debounceSearch() {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.applyFilters();
            }, 300);
        },
        
        async applyFilters() {
            this.currentPage = 1; // Reset to first page when filtering
            console.log('=== APPLYING FILTERS ===');
            console.log('Current filters:', JSON.stringify(this.filters, null, 2));
            console.log('About to call loadJobs()...');
            await this.loadJobs();
            console.log('loadJobs() completed, total jobs:', this.jobs.length);
        },
        
        clearFilters() {
            this.filters = {
                search: '',
                location: '',
                visa_sponsorship: '',
                experience_level: '',
                student_friendly: false,
                source: ''
            };
            this.currentPage = 1;
            this.applyFilters();
        },
        
        hasActiveFilters() {
            return this.filters.search.trim() !== '' ||
                   this.filters.location !== '' ||
                   this.filters.visa_sponsorship !== '' ||
                   this.filters.experience_level !== '' ||
                   this.filters.student_friendly === true ||
                   this.filters.source !== '';
        },
        
        sortJobs() {
            this.currentPage = 1; // Reset to first page when sorting
        },
        
        formatSalary(amount) {
            if (!amount) return '0';
            return new Intl.NumberFormat('en-AU').format(amount);
        },
        
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleDateString('en-AU');
        },
        
        getVisaConfidenceColor(confidence) {
            if (confidence >= 0.8) return 'text-green-600';
            if (confidence >= 0.6) return 'text-yellow-600';
            return 'text-red-600';
        },
        
        getExperienceLevelBadge(level) {
            const badges = {
                'entry': 'bg-green-100 text-green-800',
                'mid': 'bg-blue-100 text-blue-800',
                'senior': 'bg-purple-100 text-purple-800'
            };
            return badges[level] || 'bg-gray-100 text-gray-800';
        }
    };
}
