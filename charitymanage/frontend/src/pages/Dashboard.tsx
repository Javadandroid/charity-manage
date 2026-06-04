import React, { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const downloadReport = async (endpoint: string, filename: string) => {
    setLoading(endpoint);
    setError(null);
    try {
      // In a real app, you might need to send auth tokens here
      const response = await axios.get(`${API_URL}/api/reports/${endpoint}/`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      console.error("Error downloading report", err);
      setError("خطا در دانلود گزارش. لطفاً مطمئن شوید دسترسی لازم را دارید.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="bg-white rounded-3xl p-6 md:p-8 shadow-xl border border-slate-100">
      <h2 className="text-3xl font-bold text-slate-800 mb-8 border-b border-slate-100 pb-4">
        داشبورد مدیریت و گزارشات
      </h2>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 border border-red-100">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Market Report Card */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-2xl p-6 hover:shadow-lg transition-shadow">
          <div className="w-12 h-12 bg-blue-500 text-white rounded-xl flex items-center justify-center mb-4 shadow-md">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-800 mb-2">گزارش فروش بازارچه</h3>
          <p className="text-slate-500 mb-6 text-sm">دانلود گزارش جامع اکسل شامل فروش کل و فروش روزانه به تفکیک غرفه‌ها.</p>
          <button 
            onClick={() => downloadReport('market', 'market_report.xlsx')}
            disabled={loading === 'market'}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-3 px-4 rounded-xl transition-colors flex justify-center items-center"
          >
            {loading === 'market' ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : 'دانلود گزارش اکسل'}
          </button>
        </div>

        {/* Product Sales Report Card */}
        <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 rounded-2xl p-6 hover:shadow-lg transition-shadow">
          <div className="w-12 h-12 bg-emerald-500 text-white rounded-xl flex items-center justify-center mb-4 shadow-md">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-800 mb-2">گزارش فروش محصولات</h3>
          <p className="text-slate-500 mb-6 text-sm">دانلود آمار دقیق فروش هر محصول به همراه قیمت واحد و غرفه مربوطه.</p>
          <button 
            onClick={() => downloadReport('product-sales', 'product_sales_report.xlsx')}
            disabled={loading === 'product-sales'}
            className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-300 text-white font-medium py-3 px-4 rounded-xl transition-colors flex justify-center items-center"
          >
            {loading === 'product-sales' ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : 'دانلود گزارش اکسل'}
          </button>
        </div>

        {/* Customer Phones Report Card */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-100 rounded-2xl p-6 hover:shadow-lg transition-shadow">
          <div className="w-12 h-12 bg-purple-500 text-white rounded-xl flex items-center justify-center mb-4 shadow-md">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
          </div>
          <h3 className="text-xl font-bold text-slate-800 mb-2">گزارش شماره مشتریان</h3>
          <p className="text-slate-500 mb-6 text-sm">لیست شماره موبایل، نام و مبالغ خرید مشتریان تجمیع شده از تمامی غرفه‌ها.</p>
          <button 
            onClick={() => downloadReport('customer-phones', 'customer_phones_report.xlsx')}
            disabled={loading === 'customer-phones'}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 text-white font-medium py-3 px-4 rounded-xl transition-colors flex justify-center items-center"
          >
            {loading === 'customer-phones' ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : 'دانلود گزارش اکسل'}
          </button>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
