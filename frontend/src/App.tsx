import { useMemo, useState } from 'react';

type PlanWeek = {
  week_number: number;
  curriculum_item: string | null;
  status: string;
  holiday_names: string[];
};

const initialPlan: PlanWeek[] = [
  {
    week_number: 1,
    curriculum_item: 'Matematik / 6 / Kesirler / Hafta 1: Kesirleri tanır.',
    status: 'planned',
    holiday_names: [],
  },
  {
    week_number: 2,
    curriculum_item: null,
    status: 'holiday',
    holiday_names: ['Milli Mücadele'],
  },
];

function App() {
  const [subject, setSubject] = useState('Matematik');
  const [gradeLevel, setGradeLevel] = useState('6');
  const [academicYear, setAcademicYear] = useState('2025-2026');
  const [weeks, setWeeks] = useState<PlanWeek[]>(initialPlan);

  const summary = useMemo(() => {
    const plannedCount = weeks.filter((week) => week.status === 'planned').length;
    const holidayCount = weeks.filter((week) => week.status === 'holiday').length;
    return `${plannedCount} haftalık ders planı, ${holidayCount} tatil/ara tatil haftası`;
  }, [weeks]);

  const handleGenerate = () => {
    const generated = initialPlan.map((week, index) => ({
      ...week,
      week_number: index + 1,
      curriculum_item:
        week.status === 'holiday'
          ? null
          : `${subject} / ${gradeLevel} / Hafta ${index + 1}: ${subject} kazanımı`,
    }));
    setWeeks(generated);
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: 24, maxWidth: 980, margin: '0 auto' }}>
      <h1>MEB Uyumlu Plan Sihirbazı</h1>
      <p>Öğretmenlerin ders planlarını ve resmi evraklarını tek ekrandan yönetmesi için MVP arayüz.</p>

      <section style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', marginBottom: 24 }}>
        <label>
          <div>Ders</div>
          <input value={subject} onChange={(event) => setSubject(event.target.value)} style={{ width: '100%', padding: 8 }} />
        </label>
        <label>
          <div>Sınıf</div>
          <input value={gradeLevel} onChange={(event) => setGradeLevel(event.target.value)} style={{ width: '100%', padding: 8 }} />
        </label>
        <label>
          <div>Eğitim Yılı</div>
          <input value={academicYear} onChange={(event) => setAcademicYear(event.target.value)} style={{ width: '100%', padding: 8 }} />
        </label>
      </section>

      <button onClick={handleGenerate} style={{ padding: '10px 16px', cursor: 'pointer', marginBottom: 16 }}>
        Planı Oluştur
      </button>

      <p><strong>Özet:</strong> {summary}</p>

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ border: '1px solid #ccc', padding: 8, textAlign: 'left' }}>Hafta</th>
            <th style={{ border: '1px solid #ccc', padding: 8, textAlign: 'left' }}>Durum</th>
            <th style={{ border: '1px solid #ccc', padding: 8, textAlign: 'left' }}>Kazanım / Not</th>
          </tr>
        </thead>
        <tbody>
          {weeks.map((week) => (
            <tr key={week.week_number}>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{week.week_number}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{week.status}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>
                {week.curriculum_item ?? week.holiday_names.join(', ')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
