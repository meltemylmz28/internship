async function postJson(url, payload) {
  const params = new URLSearchParams(payload);
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
    body: params.toString(),
  });
  return response.json();
}

function setResult(elementId, payload) {
  document.getElementById(elementId).textContent = JSON.stringify(payload, null, 2);
}

document.getElementById('login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = {
    username: document.getElementById('username').value,
    password: document.getElementById('password').value,
  };
  const result = await postJson('/api/auth/login', payload);
  setResult('login-result', result);
});

document.getElementById('generate-plan').addEventListener('click', async () => {
  const payload = {
    academic_year: document.getElementById('academic-year').value,
    subject: document.getElementById('subject').value,
    grade_level: document.getElementById('grade-level').value,
    weeks_limit: '4',
    curriculum_items: JSON.stringify([
      {
        subject: document.getElementById('subject').value,
        grade_level: document.getElementById('grade-level').value,
        unit: 'Kesirler',
        week: 1,
        learning_outcome: 'Kesirleri tanır.',
      },
    ]),
  };
  const result = await postJson('/api/plans/generate', payload);
  setResult('plan-result', result);
});

document.getElementById('generate-document').addEventListener('click', async () => {
  const payload = {
    template_name: document.getElementById('template-name').value,
    document_type: document.getElementById('document-type').value,
    filled_data: JSON.stringify({
      club_name: 'Yeşilay Kulübü',
      teacher_name: 'Ayşe Yılmaz',
    }),
  };
  const result = await postJson('/api/documents/generate', payload);
  setResult('document-result', result);
});
