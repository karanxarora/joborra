# Production Google OAuth Setup for joborra.com

## Environment Variables for Production

Update your production `.env` file with:

```bash
# Production Google OAuth Configuration
GOOGLE_CLIENT_ID=1089724647257-jd4cc3c02e7ka975ij47mni56eubvisu.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=https://joborra.com/api/auth/google/callback
FRONTEND_ORIGIN=https://joborra.com

# Production API URL
REACT_APP_API_URL=https://joborra.com/api
```

## Google OAuth Console Configuration

### 1. Authorized JavaScript Origins
Add these to your Google OAuth Console:
```
https://joborra.com
```

### 2. Authorized Redirect URIs
Add these to your Google OAuth Console:
```
https://joborra.com/api/auth/google/callback
```

## Frontend Production Configuration

Update `frontend/.env.production`:
```bash
REACT_APP_API_URL=https://joborra.com/api
REACT_APP_GOOGLE_CLIENT_ID=1089724647257-jd4cc3c02e7ka975ij47mni56eubvisu.apps.googleusercontent.com
```

## Testing Production Setup

1. **Deploy your application** to `joborra.com`
2. **Test Google OAuth** by visiting `https://joborra.com/api/auth/google/login`
3. **Verify redirect** - should redirect to Google, then back to `https://joborra.com/api/auth/google/callback`

## Common Production Issues

### Issue: "redirect_uri_mismatch"
- **Cause**: Google OAuth Console doesn't have the production redirect URI
- **Solution**: Add `https://joborra.com/api/auth/google/callback` to Authorized Redirect URIs

### Issue: "invalid_client"
- **Cause**: Client ID not configured for production domain
- **Solution**: Add `https://joborra.com` to Authorized JavaScript Origins

### Issue: "access_denied"
- **Cause**: Domain not authorized in Google Console
- **Solution**: Verify all production URLs are added to Google OAuth Console

## Security Considerations

1. **HTTPS Only**: Production must use HTTPS for Google OAuth
2. **Domain Verification**: Ensure `joborra.com` is verified in Google Console
3. **Client Secret**: Keep `GOOGLE_CLIENT_SECRET` secure and never expose it in frontend code

## Quick Checklist

- [ ] Update production `.env` with correct URLs
- [ ] Add `https://joborra.com` to Authorized JavaScript Origins
- [ ] Add `https://joborra.com/api/auth/google/callback` to Authorized Redirect URIs
- [ ] Update frontend production environment variables
- [ ] Test Google OAuth flow in production
- [ ] Verify HTTPS is working correctly

## Current Working Configuration (Local)

Your local setup is now working with:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Google OAuth: `http://localhost:8000/api/auth/google/callback`

This same pattern will work in production with `joborra.com` domain.
