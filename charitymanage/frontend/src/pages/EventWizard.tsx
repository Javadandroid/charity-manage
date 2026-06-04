import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { useEventStore } from '../store/useEventStore';

export default function EventWizard() {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();
  const { allEvents, fetchEvents } = useEventStore();

  // Event details
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Copy state
  const [sourceEventId, setSourceEventId] = useState<number | null>(null);
  const [sourceBooths, setSourceBooths] = useState<any[]>([]);
  const [selectedBooths, setSelectedBooths] = useState<any[]>([]); // Stores booth id and products

  useEffect(() => {
    if (sourceEventId) {
      api.get(`/api/booths/?event=${sourceEventId}`)
         .then(res => setSourceBooths(res.data))
         .catch(err => console.error(err));
    } else {
      setSourceBooths([]);
    }
  }, [sourceEventId]);

  const handleNext = () => setStep(s => s + 1);
  const handlePrev = () => setStep(s => s - 1);

  const toggleBooth = (booth: any) => {
    const exists = selectedBooths.find(b => b.booth_id === booth.id);
    if (exists) {
      setSelectedBooths(selectedBooths.filter(b => b.booth_id !== booth.id));
    } else {
      // Fetch products for this booth to copy
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
      navigate('/');
    } catch (error) {
      console.error('Failed to create event', error);
      alert('خطا در ایجاد رویداد');
    }
  };

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 border-b pb-4">ایجاد رویداد جدید (مرحله {step} از 3)</h2>

      {step === 1 && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">نام رویداد</label>
            <input type="text" className="w-full border border-gray-300 p-2 rounded" value={name} onChange={e => setName(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">مکان</label>
            <input type="text" className="w-full border border-gray-300 p-2 rounded" value={location} onChange={e => setLocation(e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تاریخ شروع</label>
              <input type="date" className="w-full border border-gray-300 p-2 rounded" value={startDate} onChange={e => setStartDate(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">تاریخ پایان</label>
              <input type="date" className="w-full border border-gray-300 p-2 rounded" value={endDate} onChange={e => setEndDate(e.target.value)} />
            </div>
          </div>
          <button onClick={handleNext} disabled={!name || !startDate || !endDate} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">بعدی</button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <p className="text-gray-600 mb-4">آیا می‌خواهید اطلاعات را از یک رویداد قبلی کپی کنید؟</p>
          <select
            className="w-full border border-gray-300 p-2 rounded mb-6"
            value={sourceEventId || ''}
            onChange={e => setSourceEventId(Number(e.target.value) || null)}
          >
            <option value="">خیر، یک رویداد خالی می‌خواهم</option>
            {allEvents.map(e => (
              <option key={e.id} value={e.id}>{e.name}</option>
            ))}
          </select>

          {sourceEventId && sourceBooths.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2 text-gray-800">انتخاب غرفه‌ها برای انتقال:</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto border p-4 rounded bg-gray-50">
                {sourceBooths.map(booth => (
                  <label key={booth.id} className="flex items-center space-x-2 space-x-reverse">
                    <input
                      type="checkbox"
                      checked={!!selectedBooths.find(b => b.booth_id === booth.id)}
                      onChange={() => toggleBooth(booth)}
                      className="rounded border-gray-300 text-blue-600"
                    />
                    <span>{booth.name}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="flex space-x-4 space-x-reverse mt-6">
            <button onClick={handlePrev} className="px-6 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">قبلی</button>
            <button onClick={handleNext} className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">بعدی</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-6">
          <h3 className="font-semibold text-gray-800">بررسی و ویرایش محصولات:</h3>
          {selectedBooths.length === 0 ? (
            <p className="text-gray-500">هیچ غرفه‌ای برای کپی انتخاب نشده است.</p>
          ) : (
            selectedBooths.map(booth => (
              <div key={booth.booth_id} className="border border-gray-200 rounded p-4">
                <h4 className="font-bold text-blue-800 mb-3">{booth.name}</h4>
                <div className="space-y-3">
                  {booth.products.map((p: any) => (
                    <div key={p.product_id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                      <label className="flex items-center space-x-2 space-x-reverse w-1/2">
                        <input type="checkbox" checked={p.selected} onChange={() => toggleProduct(booth.booth_id, p.product_id)} />
                        <span className="truncate">{p.name}</span>
                      </label>
                      <div className="flex items-center space-x-2 space-x-reverse w-1/2 justify-end">
                        <span className="text-sm text-gray-500">قیمت جدید:</span>
                        <input
                          type="number"
                          disabled={!p.selected}
                          value={p.new_price}
                          onChange={(e) => handleProductPriceChange(booth.booth_id, p.product_id, Number(e.target.value))}
                          className="border border-gray-300 p-1 w-32 rounded text-left"
                          dir="ltr"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}

          <div className="flex space-x-4 space-x-reverse mt-6">
            <button onClick={handlePrev} className="px-6 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">قبلی</button>
            <button onClick={submitWizard} className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700">ثبت رویداد و انتقال اطلاعات</button>
          </div>
        </div>
      )}
    </div>
  );
}
