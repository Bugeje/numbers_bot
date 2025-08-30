# 🚀 Quick Start: Testing Performance Optimizations

## 1. Environment Setup

Add these optimized settings to your `.env` file:

```env
# Core Performance Settings
MAX_CONCURRENT_REQUESTS=200
THREAD_POOL_SIZE=100
AI_SEMAPHORE_LIMIT=50
PDF_SEMAPHORE_LIMIT=30
HTTP_TIMEOUT=45.0
CONNECTION_POOL_SIZE=200

# Your existing settings
TELEGRAM_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here
```

## 2. Quick Performance Test

### Test with 10 Users (Light Load)
```bash
python tools/stress_test.py --users 10 --duration 60
```

### Test with 50 Users (Medium Load)
```bash
python tools/stress_test.py --users 50 --duration 120
```

### Test with 100 Users (High Load)
```bash
python tools/stress_test.py --users 100 --duration 300 --output test_results.json
```

## 3. Real-time Monitoring

### Start Performance Dashboard
```bash
python tools/performance_dashboard.py
```

### One-time Status Check
```bash
python tools/performance_dashboard.py --once
```

### Export Current Metrics
```bash
python tools/performance_dashboard.py --export metrics.json
```

## 4. Expected Results

### ✅ Success Criteria for 100 Users:
- **Requests/sec**: > 5 RPS
- **Average Response Time**: < 5 seconds
- **Success Rate**: > 95%
- **Memory Usage**: < 1GB
- **No queue delays for users**

### 🎯 Performance Targets:
- **Excellent**: > 10 RPS, < 2s avg response
- **Good**: 5-10 RPS, 2-5s avg response  
- **Needs Work**: < 5 RPS, > 5s avg response

## 5. Quick Troubleshooting

### If You See High Error Rates:
1. Check your OpenRouter API key
2. Verify internet connection
3. Monitor rate limits

### If Response Times Are Slow:
1. Check AI API response times
2. Monitor PDF generation queue
3. Increase semaphore limits if needed

### If Memory Usage Is High:
1. Check temporary file count
2. Monitor cache usage
3. Restart if memory keeps growing

## 6. Before/After Comparison

Run the same test before and after applying optimizations to see the improvement:

```bash
# Save results for comparison
python tools/stress_test.py --users 50 --duration 120 --output before_optimization.json
# Apply optimizations, then:
python tools/stress_test.py --users 50 --duration 120 --output after_optimization.json
```

## 7. Production Deployment

When ready for production with the optimizations:

1. Update your `.env` with the optimized settings
2. Restart the bot
3. Monitor performance dashboard for first hour
4. Gradually increase user load
5. Adjust semaphore limits based on server capacity

---

**🎉 You should now see dramatically improved performance supporting 100+ concurrent users without queueing delays!**