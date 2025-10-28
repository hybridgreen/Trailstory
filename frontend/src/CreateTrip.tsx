export default function CreateTrip({ children }) {
  return <div className="create-trip">{children}</div>;
}

function TripFrom() {
  function draftTrip(formData: FormData) {
    const title = formData.get("title");
    const description = formData.get("description");
    const start_date: str = formData.get("start_date");
    const end_date: str = formData.get("end_date");

    if (end_date && Date.parse(end_date) < Date.parse(start_date)) {
      alert("End date cannot be before start date");
    }
  }

  return (
    <div>
      <form action={draftTrip}>
        <div>
          <label>Title</label>
        </div>
        <div>
          <input name="title" />
        </div>
        <div>
          <label>Description</label>
        </div>
        <div>
          <input name="description" />
        </div>
        <div>
          <span>
            Trip date
            <input> name= "start_date"</input>
          </span>
        </div>
        <div>
          <button type="submit"> Sign Up</button>
        </div>
      </form>
    </div>
  );
}

function RideUpload() {}

function RideCard() {}
