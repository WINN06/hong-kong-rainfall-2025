# Process

## Tools

I used Codex to read the assignment brief and week 3 examples, compare possible data sources, write the first versions of `fetch.py` and `plot.py`, and run the scripts while checking the output. I used the Open-Meteo Historical Weather API for the published data and Matplotlib to draw the final static image.

## Kept

I kept the month-by-day heatmap because it preserves every daily value and makes both the wet season and isolated heavy-rain days visible. I also kept a separate bar for each monthly total. The bars answer a broader seasonal question without asking the viewer to estimate totals from colour alone. After reviewing the first plot, I added orange outlines around the five wettest days so the main claim in the title is visible in the picture itself.

## Rejected and corrected

I rejected an animation or interactive web map. Those formats would add technical complexity but would not answer the question better because this dataset has only a date, one location and one rainfall amount per day. I also avoided a simple line chart: it would show peaks accurately, but overlapping 365 points would make long dry periods and month-to-month structure harder to scan.

An early description treated the values as direct rainfall measurements. After checking the Open-Meteo documentation, I corrected this wording because the historical values are reanalysis data, combining observations with weather models. The remaining limitation is that the chosen API value represents one coordinate rather than every district in Hong Kong.

