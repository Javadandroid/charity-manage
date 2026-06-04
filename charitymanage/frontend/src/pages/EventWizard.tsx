import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useEventStore } from '../store/useEventStore';
import { useToastStore } from '../store/useToastStore';

export default function EventWizard() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const { allEvents, fetchEvents } = useEventStore();
  const { addToast } = useToastStore();

  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const [sourceEventId, setSourceEventId] = useState<number | null>(null);
  const [sourceBooths, setSourceBooths] = useState<any[]>([]);
  const [selectedBooths, setSelectedBooths] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (sourceEventId) {
      api.get(`/api/booths/?event=${sourceEventId}`)
         .then(res => setSourceBooths(res.data))
         .catch(err => console.error(err));
    } else {
      setSourceBooths([]);
      setSelectedBooths([]);
    }
  }, [sourceEventId]);

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const toggleBooth = (booth: any) => {
    const exists = selectedBooths.find(b => b.booth_id === booth.id);
    if (exists) {
      setSelectedBooths(selectedBooths.filter(b => b.booth_id !== booth.id));
    } else {
      api.get(`/api/products/?booth=${booth.id}`).then(res => {
        setSelectedBooths([...selectedBooths, {
          booth_id: booth.id,
          name: booth.name,
          products: res.data.map((p: any) => ({ product_id: p.id, name: p.name, new_price: p.price, selected: true })),
          pos_devices: booth.pos_devices?.map((pos: any) => pos.id) || []
        }]);
      });
    }
  };

  const handleProductPriceChange = (boothId: number, productId: number, price: number) => {
    setSelectedBooths(selectedBooths.map(b => {
      if (b.booth_id === boothId) {
        return {
          ...b,
          products: b.products.map((p: any) => p.product_id === productId ? { ...p, new_price: price } : p)
        };
      }
      return b;
    }));
  };

  const toggleProduct = (boothId: number, productId: number) => {
     setSelectedBooths(selectedBooths.map(b => {
      if (b.booth_id === boothId) {
        return {
          ...b,
          products: b.products.map((p: any) => p.product_id === productId ? { ...p, selected: !p.selected } : p)
        };
      }
      return b;
    }));
  };

  const submitWizard = async () => {
    setLoading(true);
    const payload = {
      name,
      location,
      start_date: startDate,
      end_date: endDate,
      source_event_id: sourceEventId,
      booths_to_copy: selectedBooths.map(b => ({
        booth_id: b.booth_id,
        products: b.products.filter((p: any) => p.selected).map((p: any) => ({
          product_id: p.product_id,
          new_price: p.new_price
        })),
        pos_devices: b.pos_devices
      }))
    };

    try {
      await api.post('/api/events/wizard/', payload);
      await fetchEvents();
      addToast('رویداد با موفقیت ایجاد شد', 'success');
      navigate('/');
    } catch (error) {
      console.error('Failed to create event', error);
      addToast('خطا در ایجاد رویداد', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
      <div className="flex justify-between items-center mb-8 border-b pb-4">
        <div>
          <h2 className="text-3xl font-black text-gray-800 tracking-tight">ایجاد رویداد جدید</h2>
          <p className="text-gray-500 mt-1">مرحله {step} از 3</p>
        </div>

        <div className="flex space-x-2 space-x-reverse">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>1</div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>2</div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>3</div>
        </div>
      </div>

      {step === 1 && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">نام رویداد</label>
            <input type="text" className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 transition" value={name} onChange={e => setName(e.target.value)} placeholder="مثال: بازارچه تابستانه 1403" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">مکان</label>
            <input type="text" className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 transition" value={location} onChange={e => setLocation(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">تاریخ شروع</label>
              <input type="date" className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 transition" value={startDate} onChange={e => setStartDate(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">تاریخ پایان</label>
              <input type="date" className="w-full border border-gray-300 p-3 rounded-xl focus:ring-2 focus:ring-blue-500 transition" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>
          </div>
          <div className="pt-4 flex justify-end">
            <button onClick={handleNext} disabled={!name || !startDate || !endDate} className="px-8 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 disabled:opacity-50 transition shadow-md">ادامه (مرحله بعد)</button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-6">
          <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
            <h3 className="font-bold text-blue-800 mb-2">آیا می‌خواهید اطلاعات غرفه‌ها و محصولات را از رویدادهای قبلی کپی کنید؟</h3>
            <p className="text-sm text-blue-600 mb-4">با انتخاب یک رویداد مرجع، می‌توانید لیست غرفه‌ها را ببینید و آن‌هایی که می‌خواهید به این رویداد منتقل شوند را تیک بزنید.</p>
            <select
              className="w-full border border-blue-200 p-3 rounded-xl bg-white"
              value={sourceEventId || ''}
              onChange={e => setSourceEventId(Number(e.target.value) || null)}
            >
              <option value="">خیر، یک رویداد خالی می‌خواهم بسازم</option>
              {allEvents.map(e => (
                <option key={e.id} value={e.id}>{e.name}</option>
              ))}
            </select>
          </div>

          {sourceEventId && sourceBooths.length > 0 && (
            <div className="mt-6">
              <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                <svg className="w-5 h-5 ml-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                غرفه‌های رویداد مبدا:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-80 overflow-y-auto custom-scrollbar p-2">
                {sourceBooths.map(booth => {
                  const isSelected = !!selectedBooths.find(b => b.booth_id === booth.id);
                  return (
                    <label key={booth.id} className={`flex items-center space-x-3 space-x-reverse p-4 rounded-xl border-2 transition cursor-pointer ${isSelected ? 'border-blue-500 bg-blue-50/50' : 'border-gray-200 hover:border-blue-300'}`}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleBooth(booth)}
                        className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="font-bold text-gray-700">{booth.name}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          <div className="flex justify-between pt-6 border-t mt-8">
            <button onClick={handlePrev} className="px-6 py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition">بازگشت</button>
            <button onClick={handleNext} className="px-8 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition shadow-md">ادامه (مرحله بعد)</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-6">
          <div className="bg-yellow-50 p-4 rounded-xl border border-yellow-200 mb-6">
            <p className="text-sm font-semibold text-yellow-800">در این مرحله می‌توانید تعیین کنید کدام محصولاتِ غرفه‌های انتخاب‌شده منتقل شوند و قیمت جدید آن‌ها را در صورت نیاز ویرایش کنید.</p>
          </div>

          {selectedBooths.length === 0 ? (
            <div className="text-center p-10 bg-gray-50 rounded-2xl border border-dashed border-gray-300">
              <p className="text-gray-500 font-medium">هیچ غرفه‌ای برای کپی انتخاب نشده است. رویداد شما خالی ایجاد خواهد شد.</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar pr-2">
              {selectedBooths.map(booth => (
                <div key={booth.booth_id} className="border border-gray-200 rounded-2xl p-5 bg-white shadow-sm">
                  <h4 className="font-black text-indigo-700 mb-4 text-lg border-b pb-2">{booth.name}</h4>
                  <div className="space-y-3">
                    {booth.products.map((p: any) => (
                      <div key={p.product_id} className={`flex items-center justify-between p-3 rounded-xl transition ${p.selected ? 'bg-gray-50 border border-gray-200' : 'bg-white border border-gray-100 opacity-50'}`}>
                        <label className="flex items-center space-x-3 space-x-reverse w-1/2 cursor-pointer">
                          <input type="checkbox" checked={p.selected} onChange={() => toggleProduct(booth.booth_id, p.product_id)} className="w-4 h-4 rounded text-blue-600" />
                          <span className="font-medium text-gray-800 truncate">{p.name}</span>
                        </label>
                        <div className="flex items-center space-x-2 space-x-reverse w-1/2 justify-end">
                          <span className="text-xs text-gray-500 font-medium bg-white px-2">قیمت (تومان):</span>
                          <input
                            type="number"
                            disabled={!p.selected}
                            value={p.new_price}
                            onChange={(e) => handleProductPriceChange(booth.booth_id, p.product_id, Number(e.target.value))}
                            className="border border-gray-300 p-2 w-32 rounded-lg text-left font-mono focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                            dir="ltr"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex justify-between pt-6 border-t mt-8">
            <button onClick={handlePrev} className="px-6 py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition">بازگشت</button>
            <button onClick={submitWizard} disabled={loading} className="px-8 py-3 bg-green-600 text-white font-bold rounded-xl hover:bg-green-700 transition shadow-lg disabled:opacity-70 flex items-center">
              {loading ? 'در حال ثبت...' : 'ثبت رویداد و انتقال اطلاعات'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
