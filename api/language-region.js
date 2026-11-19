// Vercel supplies a coarse country code at the edge. No address is stored or sent to a lookup service.
export default function handler(req, res) {
  res.setHeader('Cache-Control', 'private, no-store');
  const country = req.headers['x-vercel-ip-country'];
  const arabic = ['AE','BH','DZ','EG','IQ','JO','KW','LB','LY','MA','MR','OM','PS','QA','SA','SD','SY','TN','YE'];
  res.status(200).json({language: country === 'CN' ? 'zh' : arabic.includes(country) ? 'ar' : null});
}
