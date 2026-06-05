import { useState, useEffect, useRef } from 'react';
import { useEventStore } from '../store/useEventStore';
import api from '../api';

interface KioskInvoice {
  id: number;
  invoice_number: string;
  customer_name: string;
  booth_name: string;
}

export default function Kiosk() {
  const { activeEvent, fetchEvents } = useEventStore();
  const [invoices, setInvoices] = useState<KioskInvoice[]>([]);
  const [lastCalled, setLastCalled] = useState<KioskInvoice | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Track seen IDs to only play audio for new ones
  const previousInvoicesIds = useRef<Set<number>>(new Set());

  // Kiosk is independent and might be opened in a new tab, so fetch events manually
  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const fetchInvoices = async () => {
    if (!activeEvent) return;
    try {
      // The backend has ?status=ready filtered to `is_paid=True`
      // We will add the related fields (booth_name, etc) in backend or just use customer_name
      // Actually backend InvoiceSerializer doesn't return booth_name by default, we need to handle it.
      const res = await api.get(`/api/invoices/?event=${activeEvent.id}&status=ready`);
      const fetchedInvoices: KioskInvoice[] = res.data.map((inv: any) => ({
        id: inv.id,
        invoice_number: inv.invoice_number,
        customer_name: inv.customer_name,
        booth_name: inv.booth_name || 'غرفه' // Mock fallback if backend serializer is not customized
      }));

      setInvoices(fetchedInvoices);

      // Determine if there is a new invoice
      const currentIds = new Set(fetchedInvoices.map(i => i.id));
      const newInvoices = fetchedInvoices.filter(i => !previousInvoicesIds.current.has(i.id));

      if (previousInvoicesIds.current.size > 0 && newInvoices.length > 0) {
        // Automatically call the newest one
        callNumber(newInvoices[0]);
      }

      previousInvoicesIds.current = currentIds;
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchInvoices();
    const interval = setInterval(fetchInvoices, 5000);
    return () => clearInterval(interval);
  }, [activeEvent]);

  const callNumber = async (invoice: KioskInvoice) => {
    setLastCalled(invoice);

    const numMatch = invoice.invoice_number.match(/\d+/);
    const invoiceNum = numMatch ? parseInt(numMatch[0], 10) : invoice.invoice_number;

    const textToRead = `شماره ${invoiceNum}. ${invoice.booth_name}`;

    const ttsUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/kiosk/tts/?text=${encodeURIComponent(textToRead)}`;

    if (audioRef.current) {
      audioRef.current.src = ttsUrl;
      try {
         await audioRef.current.play();
      } catch (err) {
         console.warn("Audio play failed. Browser policy might block autoplay until user interacts.", err);
      }
    }
  };

  if (!activeEvent) return <div className="p-10 text-center text-white bg-gray-900 min-h-screen flex items-center justify-center font-bold text-2xl">در حال اتصال به کیوسک...</div>;

  return (
    <div className="bg-gray-900 text-white min-h-screen rounded-none md:rounded-xl p-8 flex flex-col md:flex-row gap-8 font-sans" dir="rtl">
      <audio ref={audioRef} className="hidden" />

      {/* Latest Called Number (Big Display) */}
      <div className="md:w-1/2 flex flex-col items-center justify-center border-b md:border-b-0 md:border-l border-gray-700 pb-8 md:pb-0 relative">
        <div className="absolute top-0 left-0 p-4 opacity-50 text-xs">کیوسک هوشمند نوبت‌دهی • {activeEvent.name}</div>
        <h2 className="text-3xl text-gray-400 mb-6 font-bold tracking-widest">شماره فراخوانده شده</h2>
        {lastCalled ? (
          <div className="bg-blue-600 rounded-3xl p-12 text-center shadow-[0_0_80px_rgba(37,99,235,0.6)] w-full max-w-md transform scale-110 animate-pulse">
            <div className="text-8xl font-black font-mono mb-4 text-white drop-shadow-lg">{lastCalled.invoice_number.replace('inv', '')}</div>
            <div className="text-3xl mt-4 font-bold text-blue-100">{lastCalled.booth_name}</div>
            <div className="text-xl mt-2 text-blue-200">{lastCalled.customer_name}</div>
          </div>
        ) : (
          <div className="text-gray-500 text-3xl font-medium animate-bounce">منتظر فراخوان...</div>
        )}
      </div>

      {/* List of Waiting Numbers */}
      <div className="md:w-1/2 flex flex-col pt-8 md:pt-0 pl-0 md:pl-4">
        <h2 className="text-3xl text-green-400 mb-8 font-bold flex items-center">
          <span className="w-4 h-4 rounded-full bg-green-500 animate-ping ml-3"></span>
          آماده تحویل
        </h2>
        <div className="grid grid-cols-2 gap-5 auto-rows-max overflow-y-auto pr-2 max-h-[80vh] custom-scrollbar">
          {invoices.length > 0 ? invoices.map((inv) => (
            <div
              key={inv.id}
              onClick={() => callNumber(inv)}
              className="bg-gray-800 p-6 rounded-2xl border border-gray-700 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-700 hover:border-gray-500 transition shadow-lg relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition duration-500"></div>
              <div className="text-5xl font-black font-mono text-yellow-400 mb-2">{inv.invoice_number.replace('inv', '')}</div>
              <div className="text-lg text-gray-300 font-bold">{inv.booth_name}</div>
            </div>
          )) : (
            <div className="col-span-2 text-center text-gray-500 py-20 text-2xl font-medium">هیچ سفارشی آماده تحویل نیست.</div>
          )}
        </div>
      </div>
    </div>
  );
}
