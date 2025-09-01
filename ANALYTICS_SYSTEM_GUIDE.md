# Joborra Analytics System Guide

## Overview

The Joborra Analytics System provides comprehensive data export and analysis capabilities for your SQLite database. It exports user data, job analytics, and application metrics to structured documents stored in Supabase.

## 🎯 Features

### ✅ **Data Export Capabilities**
- **User Analytics**: Registration trends, role breakdowns, activity metrics
- **Job Analytics**: Job statistics, categories, locations, salary data
- **Application Analytics**: Application trends and statistics
- **Multiple Formats**: JSON for APIs, CSV for spreadsheet analysis

### ✅ **Storage & Access**
- **Supabase Integration**: Secure cloud storage in `analytics-exports` bucket
- **Public Access**: Files accessible via direct URLs
- **Organized Structure**: Timestamped folders for easy management

### ✅ **Automation**
- **Manual Export**: Run exports on-demand
- **Periodic Export**: Daily, weekly, monthly automated exports
- **Dashboard**: View and analyze exported data

## 📊 Current Analytics Data

Based on your latest export:

### **User Statistics**
- **Total Users**: 23 (1 Admin, 8 Employers, 14 Students)
- **Active Users**: 23 (100% active rate)
- **Recent Growth**: 13 new users in last 7 days

### **Job Statistics**
- **Total Jobs**: 917
- **Active Jobs**: 917
- **Average Salary**: $51,780 - $71,053
- **Top Categories**: Study Aligned Professional (8), Service/Retail/Hospitality (3)

### **Geographic Distribution**
- **Top Locations**: Toronto (14), Remote (11), Sydney (8)
- **International Presence**: Jobs in Canada, US, Australia

## 🚀 Usage Guide

### **1. Manual Export**
```bash
# Run a complete analytics export
python analytics_export.py
```

### **2. Periodic Exports**
```bash
# Run daily export
python periodic_analytics.py --mode daily

# Run weekly export
python periodic_analytics.py --mode weekly

# Run monthly export
python periodic_analytics.py --mode monthly

# Start automated scheduler
python periodic_analytics.py --mode scheduler
```

### **3. View Analytics Dashboard**
```bash
# View latest analytics data
python analytics_dashboard.py
```

## 📁 File Structure

### **Exported Files**
Each export creates a timestamped folder with:
- `analytics_summary.json` - Overview and key metrics
- `user_analytics.json` - Detailed user statistics
- `job_analytics.json` - Job market analysis
- `application_analytics.json` - Application trends
- `user_details_YYYYMMDD_HHMMSS.csv` - User data for spreadsheet analysis
- `registration_trends_YYYYMMDD_HHMMSS.csv` - Registration trends

### **Storage Location**
```
Supabase Bucket: analytics-exports
├── analytics_20250901_002540/
│   ├── analytics_summary.json
│   ├── user_analytics.json
│   ├── job_analytics.json
│   ├── application_analytics.json
│   ├── user_details_20250901_002540.csv
│   └── registration_trends_20250901_002540.csv
└── analytics_YYYYMMDD_HHMMSS/ (future exports)
```

## 🔧 Configuration

### **Environment Variables**
```bash
SUPABASE_URL=https://noupavjvuhezvzpqcbqg.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
```

### **Database Connection**
- Uses SQLite database: `./joborra.db`
- Connects via SQLAlchemy ORM
- Supports all existing user and job tables

## 📈 Analytics Metrics

### **User Metrics**
- Total users by role (Admin, Employer, Student)
- Active vs inactive users
- Verification status
- Registration trends (daily, weekly, monthly)
- User engagement (resume uploads, profile completion)

### **Job Metrics**
- Total jobs posted
- Active vs expired jobs
- Job categories and distribution
- Geographic distribution
- Salary ranges and averages
- Jobs with documents

### **Application Metrics**
- Total applications
- Application trends
- Success rates
- Time-to-application analysis

## 🎯 Use Cases

### **Business Intelligence**
- Track user growth and engagement
- Monitor job market trends
- Analyze geographic expansion
- Measure platform adoption

### **Reporting**
- Generate executive summaries
- Create investor reports
- Track KPIs and metrics
- Monitor user acquisition

### **Data Analysis**
- Export to Excel/Google Sheets
- Create visualizations
- Perform statistical analysis
- Identify trends and patterns

## 🔄 Automation Setup

### **Cron Job Example**
```bash
# Add to crontab for daily exports at 2 AM
0 2 * * * cd /path/to/joborra && python periodic_analytics.py --mode daily

# Weekly exports on Sundays at 3 AM
0 3 * * 0 cd /path/to/joborra && python periodic_analytics.py --mode weekly

# Monthly exports on 1st at 4 AM
0 4 1 * * cd /path/to/joborra && python periodic_analytics.py --mode monthly
```

### **Docker Integration**
```dockerfile
# Add to your Dockerfile
COPY analytics_export.py /app/
COPY periodic_analytics.py /app/
COPY analytics_dashboard.py /app/

# Run periodic exports in container
CMD ["python", "periodic_analytics.py", "--mode", "scheduler"]
```

## 🔒 Security & Privacy

### **Data Protection**
- Analytics bucket is public for easy access
- No sensitive user data (passwords, personal info) in exports
- Anonymized user IDs for privacy
- Structured data only (no free-form text)

### **Access Control**
- Service key required for uploads
- Public read access for downloads
- Timestamped exports for audit trail

## 📊 Sample Analytics Output

### **Summary Report**
```json
{
  "export_timestamp": "2025-09-01T00:25:40",
  "summary": {
    "total_users": 23,
    "active_users": 23,
    "total_jobs": 917,
    "active_jobs": 917,
    "total_applications": 0
  },
  "user_breakdown": [
    {"role": "STUDENT", "total_users": 14, "active_users": 14},
    {"role": "EMPLOYER", "total_users": 8, "active_users": 8},
    {"role": "ADMIN", "total_users": 1, "active_users": 1}
  ]
}
```

## 🎉 Benefits

### **For Business**
- **Data-Driven Decisions**: Access to comprehensive user and job data
- **Growth Tracking**: Monitor platform adoption and user engagement
- **Market Analysis**: Understand job market trends and opportunities
- **Performance Metrics**: Track KPIs and business objectives

### **For Development**
- **User Insights**: Understand user behavior and preferences
- **Feature Usage**: Track which features are most popular
- **Geographic Expansion**: Identify new markets and opportunities
- **Product Optimization**: Data to guide product improvements

## 🚀 Next Steps

1. **Set up automated exports** using cron jobs or scheduler
2. **Create custom dashboards** using the exported JSON data
3. **Integrate with BI tools** like Tableau, Power BI, or Google Data Studio
4. **Set up alerts** for important metrics and trends
5. **Create reports** for stakeholders and investors

The analytics system is now fully operational and ready to provide valuable insights into your Joborra platform! 🎯
