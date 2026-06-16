import 'package:flutter/material.dart';
import '../data/countries.dart';
import '../widgets/clock_widget.dart';
import '../widgets/comparison_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Country _selectedCountry = kCountries.first;
  final List<Country> _comparisonList = [
    kCountries.firstWhere((c) => c.name == 'Türkiye'),
    kCountries.firstWhere((c) => c.name == 'İngiltere'),
    kCountries.firstWhere((c) => c.name == 'Japonya'),
  ];

  void _showCountryPicker() {
    String query = '';
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1a1a2e),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return StatefulBuilder(builder: (ctx, setModalState) {
          final filtered = query.isEmpty
              ? kCountries
              : kCountries
                  .where((c) => c.name.toLowerCase().contains(query.toLowerCase()))
                  .toList();
          return DraggableScrollableSheet(
            expand: false,
            initialChildSize: 0.75,
            maxChildSize: 0.95,
            builder: (_, controller) => Column(
              children: [
                const SizedBox(height: 12),
                Container(
                  width: 40, height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFF3a3a6a),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 16),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: TextField(
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Ülke ara...',
                      hintStyle: const TextStyle(color: Color(0xFF606080)),
                      prefixIcon: const Icon(Icons.search, color: Color(0xFF606080)),
                      filled: true,
                      fillColor: const Color(0xFF16213e),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (v) => setModalState(() => query = v),
                  ),
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: ListView.builder(
                    controller: controller,
                    itemCount: filtered.length,
                    itemBuilder: (_, i) {
                      final c = filtered[i];
                      final isSelected = c.timezone == _selectedCountry.timezone;
                      return ListTile(
                        leading: Text(c.flag, style: const TextStyle(fontSize: 24)),
                        title: Text(
                          c.name,
                          style: TextStyle(
                            color: isSelected ? const Color(0xFF00d4ff) : Colors.white,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                        subtitle: Text(
                          c.timezone,
                          style: const TextStyle(color: Color(0xFF606080), fontSize: 12),
                        ),
                        trailing: isSelected
                            ? const Icon(Icons.check_circle, color: Color(0xFF00d4ff))
                            : null,
                        onTap: () {
                          setState(() => _selectedCountry = c);
                          Navigator.pop(ctx);
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        });
      },
    );
  }

  void _showAddComparison() {
    String query = '';
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1a1a2e),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return StatefulBuilder(builder: (ctx, setModalState) {
          final filtered = query.isEmpty
              ? kCountries
              : kCountries
                  .where((c) => c.name.toLowerCase().contains(query.toLowerCase()))
                  .toList();
          return DraggableScrollableSheet(
            expand: false,
            initialChildSize: 0.75,
            maxChildSize: 0.95,
            builder: (_, controller) => Column(
              children: [
                const SizedBox(height: 12),
                Container(
                  width: 40, height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFF3a3a6a),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Karşılaştırma için ülke ekle',
                  style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: TextField(
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Ülke ara...',
                      hintStyle: const TextStyle(color: Color(0xFF606080)),
                      prefixIcon: const Icon(Icons.search, color: Color(0xFF606080)),
                      filled: true,
                      fillColor: const Color(0xFF16213e),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (v) => setModalState(() => query = v),
                  ),
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: ListView.builder(
                    controller: controller,
                    itemCount: filtered.length,
                    itemBuilder: (_, i) {
                      final c = filtered[i];
                      final alreadyAdded = _comparisonList.any((x) => x.timezone == c.timezone);
                      return ListTile(
                        leading: Text(c.flag, style: const TextStyle(fontSize: 24)),
                        title: Text(
                          c.name,
                          style: TextStyle(
                            color: alreadyAdded ? const Color(0xFF606080) : Colors.white,
                          ),
                        ),
                        subtitle: Text(
                          c.timezone,
                          style: const TextStyle(color: Color(0xFF606080), fontSize: 12),
                        ),
                        trailing: alreadyAdded
                            ? const Icon(Icons.check, color: Color(0xFF606080))
                            : const Icon(Icons.add_circle_outline, color: Color(0xFF00d4ff)),
                        onTap: alreadyAdded
                            ? null
                            : () {
                                setState(() => _comparisonList.add(c));
                                Navigator.pop(ctx);
                              },
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        });
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0d0d1a),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0d0d1a),
        elevation: 0,
        title: const Text(
          '🕐 Dünya Saati',
          style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Ülke seç butonu
            GestureDetector(
              onTap: _showCountryPicker,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                decoration: BoxDecoration(
                  color: const Color(0xFF1e1e3a),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFF3a3a6a)),
                ),
                child: Row(
                  children: [
                    Text(_selectedCountry.flag, style: const TextStyle(fontSize: 24)),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _selectedCountry.name,
                        style: const TextStyle(color: Colors.white, fontSize: 16),
                      ),
                    ),
                    const Icon(Icons.expand_more, color: Color(0xFF00d4ff)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Ana saat widget
            ClockWidget(country: _selectedCountry),

            const SizedBox(height: 32),

            // Karşılaştırma başlık
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Karşılaştır',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton.icon(
                  onPressed: _showAddComparison,
                  icon: const Icon(Icons.add, color: Color(0xFF00d4ff), size: 18),
                  label: const Text('Ekle', style: TextStyle(color: Color(0xFF00d4ff))),
                  style: TextButton.styleFrom(
                    backgroundColor: const Color(0xFF1e1e3a),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Karşılaştırma kartları
            if (_comparisonList.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text(
                    'Karşılaştırmak için ülke ekleyin',
                    style: TextStyle(color: Color(0xFF606080)),
                  ),
                ),
              )
            else
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: _comparisonList
                    .map((c) => ComparisonCard(
                          country: c,
                          onRemove: () {
                            setState(() => _comparisonList.remove(c));
                          },
                        ))
                    .toList(),
              ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}
